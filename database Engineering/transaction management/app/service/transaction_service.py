from decimal import Decimal
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.m_account import AccountModel
from app.schemas.transaction_schema import (
    TransferRollbackResponse,
    TransferSuccessResponse,
)


class SimulatedDatabaseError(Exception):
    """
    Custom exception used to simulate a real database or server failure.
    Raised mid-transfer when `simulate_error=True` to demonstrate that
    rollback in the `except` block undoes partial changes and preserves
    atomicity.
    """

    def __init__(self, message: str = "Simulated database connection lost"):
        self.message = message
        super().__init__(self.message)


class TransactionService:
    """
    Service layer for transfers.
    Uses `select_for_update()` (pessimistic locking) for Isolation,
    and locks accounts in a consistent order to prevent deadlocks.
    """

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _get_account_locked(
        session: AsyncSession,
        account_number: str,
    ) -> AccountModel:
        """Fetch an account by number with a row-level lock (FOR UPDATE)."""
        statement = (
            select(AccountModel)
            .where(AccountModel.account_number == account_number)
            .with_for_update()
        )
        result = await session.execute(statement)
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account '{account_number}' not found",
            )
        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account '{account_number}' is inactive",
            )
        return account

    @staticmethod
    async def _lock_accounts_in_order(
        session: AsyncSession,
        source_number: str,
        destination_number: str,
    ) -> tuple[AccountModel, AccountModel]:
        """Lock accounts in lexicographic order to prevent deadlocks."""
        if source_number < destination_number:
            first = await TransactionService._get_account_locked(session, source_number)
            second = await TransactionService._get_account_locked(
                session, destination_number
            )
            return (
                (first, second)
                if source_number == first.account_number
                else (second, first)
            )
        else:
            first = await TransactionService._get_account_locked(
                session, destination_number
            )
            second = await TransactionService._get_account_locked(
                session, source_number
            )
            return (
                (second, first)
                if source_number == second.account_number
                else (first, second)
            )

    @staticmethod
    async def _query_account(
        session: AsyncSession,
        account_number: str,
    ) -> AccountModel:
        """Simple non-locking account lookup by number."""
        statement = select(AccountModel).where(
            AccountModel.account_number == account_number
        )
        result = await session.execute(statement)
        return result.scalar_one()

    # ------------------------------------------------------------------
    # Single transfer method — try/except with rollback
    # ------------------------------------------------------------------

    @staticmethod
    async def transfer(
        session: AsyncSession,
        source_account_number: str,
        destination_account_number: str,
        amount: Decimal,
        simulate_error: bool = True,
    ) -> TransferRollbackResponse | TransferSuccessResponse:
        """
        Transfer funds between two accounts.

        **When `simulate_error=True` (default):**
          1. Lock both accounts and capture initial balances.
          2. Debit the source.
          3. Raise `SimulatedDatabaseError` (simulating a server crash).
          4. **Except block** catches the error and calls `session.rollback()`.
          5. Re-query accounts — balances are unchanged.
          6. Return `TransferRollbackResponse` proving atomicity.

        **When `simulate_error=False`:**
          1. Lock both accounts and validate balance.
          2. Debit source, credit destination.
          3. `session.commit()` — all changes durable.
          4. Return `TransferSuccessResponse` with updated balances.
        """
        if source_account_number == destination_account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different",
            )

        source, destination = await TransactionService._lock_accounts_in_order(
            session, source_account_number, destination_account_number
        )
        source_balance_before = source.balance
        destination_balance_before = destination.balance

        if source_balance_before < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient balance. "
                    f"Available: {source_balance_before}, Required: {amount}"
                ),
            )

        # Debit the source
        source.balance -= amount
        source.version += 1
        session.add(source)

        try:
            if simulate_error:
                await session.flush()
                raise SimulatedDatabaseError(
                    "Simulated database connection lost: "
                    "server crashed after debiting source, "
                    "before crediting destination."
                )

            # --- Success path: credit destination and commit ---
            destination.balance += amount
            destination.version += 1
            session.add(destination)

            await session.commit()
            await session.refresh(source)
            await session.refresh(destination)

            return TransferSuccessResponse(
                status="completed",
                message=(
                    f"Successfully transferred {amount} from "
                    f"'{source_account_number}' to "
                    f"'{destination_account_number}'."
                ),
                source_account_number=source_account_number,
                destination_account_number=destination_account_number,
                amount=amount,
                source_new_balance=source.balance,
                destination_new_balance=destination.balance,
            )

        except SimulatedDatabaseError as error:
            # ROLLBACK — undoes the partial debit, preserving atomicity
            await session.rollback()

            # Re-query to confirm both accounts are unchanged
            source_after = await TransactionService._query_account(
                session, source_account_number
            )
            destination_after = await TransactionService._query_account(
                session, destination_account_number
            )

            return TransferRollbackResponse(
                status="atomicity_preserved",
                message=(
                    f"ATOMICITY PRESERVED: {error.message} "
                    f"The `except` block called ROLLBACK, undoing the "
                    f"partial debit — both accounts returned to their "
                    f"original balances. Atomicity was maintained."
                ),
                source_account_number=source_account_number,
                destination_account_number=destination_account_number,
                amount=amount,
                source_balance_before=source_balance_before,
                source_balance_after=source_after.balance,
                destination_balance_before=destination_balance_before,
                destination_balance_after=destination_after.balance,
                atomicity_proven=(
                    source_after.balance == source_balance_before
                    and destination_after.balance == destination_balance_before
                ),
            )

    # ------------------------------------------------------------------
    # Transfer with Loyalty Bonus — demonstrates savepoints
    # ------------------------------------------------------------------

    @staticmethod
    async def transfer_with_loyalty_bonus(
        session: AsyncSession,
        source_account_number: str,
        destination_account_number: str,
        amount: Decimal,
        simulate_bonus_error: bool = False,
    ):
        """
        Transfer funds between accounts with a loyalty bonus.
        Demonstrates SQL SAVEPOINT for partial rollback.

        **How Savepoints Work:**
        - A SAVEPOINT marks a point within a transaction.
        - If an error occurs after a savepoint, ROLLBACK TO SAVEPOINT
          reverts only that portion of work, leaving earlier changes intact.
        - The outer transaction can continue or commit.

        **Flow with savepoints:**
        1. Start transaction (implicit with async session)
        2. Lock both accounts
        3. Debit source, credit destination → SAVEPOINT 'transfer_complete'
        4. Calculate and apply loyalty bonus → SAVEPOINT 'bonus_applied'
        5. If bonus fails and simulate_bonus_error=True:
           - ROLLBACK TO SAVEPOINT 'bonus_applied' (undo bonus only)
           - Transfer remains intact, commit it
        6. If all succeeds: COMMIT everything

        This shows that savepoints allow partial rollback while
        keeping the main transaction intact.
        """
        # Validate account difference
        if source_account_number == destination_account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different",
            )

        # Step 1: Lock accounts in order to prevent deadlocks
        source, destination = await TransactionService._lock_accounts_in_order(
            session, source_account_number, destination_account_number
        )
        
        source_balance_before = source.balance
        destination_balance_before = destination.balance

        # Step 2: Validate sufficient balance
        if source_balance_before < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient balance. "
                    f"Available: {source_balance_before}, Required: {amount}"
                ),
            )

        try:
            # Step 3: Perform core transfer (debit and credit)
            source.balance -= amount
            source.version += 1
            session.add(source)

            destination.balance += amount
            destination.version += 1
            session.add(destination)

            # Flush the core transfer to database
            await session.flush()

            # CREATE SAVEPOINT 'transfer_complete'
            # This marks the point after successful debit and credit
            await session.execute("SAVEPOINT transfer_complete")

            try:
                # Step 4: Apply loyalty bonus (5% of transferred amount to destination)
                bonus_amount = (amount * Decimal("0.05")).quantize(Decimal("0.01"))
                
                if bonus_amount > 0:
                    # Simulate a bonus calculation error if requested
                    if simulate_bonus_error:
                        await session.flush()
                        raise Exception(
                            "Bonus calculation service unavailable: "
                            "simulated error in loyalty system"
                        )

                    destination.balance += bonus_amount
                    destination.version += 1
                    session.add(destination)

                # Flush bonus to database
                await session.flush()

                # CREATE SAVEPOINT 'bonus_applied'
                # This marks the point after bonus was applied
                await session.execute("SAVEPOINT bonus_applied")

                # COMMIT the entire transaction (transfer + bonus)
                await session.commit()

                # Refresh to get final state
                await session.refresh(source)
                await session.refresh(destination)

                return {
                    "status": "completed",
                    "message": (
                        f"Successfully transferred {amount} from "
                        f"'{source_account_number}' to '{destination_account_number}' "
                        f"and applied {bonus_amount} loyalty bonus."
                    ),
                    "source_account_number": source_account_number,
                    "destination_account_number": destination_account_number,
                    "amount": amount,
                    "source_balance_before": source_balance_before,
                    "source_balance_after": source.balance,
                    "destination_balance_before": destination_balance_before,
                    "destination_balance_after": destination.balance,
                    "loyalty_bonus_applied": True,
                    "bonus_amount": bonus_amount,
                    "savepoint_demo": (
                        "No savepoint rollback occurred. "
                        "Both transfer and loyalty bonus were committed successfully. "
                        "Savepoints 'transfer_complete' and 'bonus_applied' reached."
                    ),
                }

            except Exception as bonus_error:
                # ROLLBACK TO SAVEPOINT 'transfer_complete'
                # This reverts the bonus but KEEPS the transfer
                await session.execute("ROLLBACK TO SAVEPOINT transfer_complete")

                # Commit the transaction with only the transfer (bonus rolled back)
                await session.commit()

                # Refresh to get final state
                await session.refresh(source)
                await session.refresh(destination)

                # Query for bonus that was applied
                bonus_amount_failed = (amount * Decimal("0.05")).quantize(Decimal("0.01"))

                return {
                    "status": "bonus_rolled_back",
                    "message": (
                        f"Transfer succeeded, but loyalty bonus failed. "
                        f"Rolled back to SAVEPOINT 'transfer_complete'. "
                        f"Transfer of {amount} is intact. "
                        f"Error: {str(bonus_error)}"
                    ),
                    "source_account_number": source_account_number,
                    "destination_account_number": destination_account_number,
                    "amount": amount,
                    "source_balance_before": source_balance_before,
                    "source_balance_after": source.balance,
                    "destination_balance_before": destination_balance_before,
                    "destination_balance_after": destination.balance,
                    "loyalty_bonus_applied": False,
                    "bonus_amount": Decimal("0.00"),
                    "savepoint_demo": (
                        f"ROLLBACK TO SAVEPOINT 'transfer_complete' was executed. "
                        f"Bonus of {bonus_amount_failed} was undone, but the transfer "
                        f"of {amount} was preserved and committed. "
                        f"This demonstrates partial rollback using savepoints!"
                    ),
                }

        except Exception as error:
            # Rollback entire transaction if something goes wrong before savepoint
            await session.rollback()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transfer with loyalty failed: {str(error)}",
            )
