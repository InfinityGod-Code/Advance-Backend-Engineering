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
