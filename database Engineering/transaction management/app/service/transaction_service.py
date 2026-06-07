from decimal import Decimal
from uuid import uuid4
from sqlmodel import select
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.m_account import AccountModel
from app.schemas.transaction_schema import (
    LoyaltyBonusResponse,
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
    ) -> LoyaltyBonusResponse:
        """
        Transfer funds with loyalty bonus using SAVEPOINTs.
        Follows the pattern:

          1. OUTER: async with session.begin()     → BEGIN / COMMIT
          2. CORE:  raw SQL UPDATE accounts         → critical transfer
          3. INNER: async with session.begin_nested() → SAVEPOINT
          4. ERROR: except DBAPIError               → ROLLBACK TO SAVEPOINT
          5. FALLBACK: raw SQL INSERT inside outer  → log failure
          6. EXIT: outer block commits transfer

        When `simulate_bonus_error=True` the savepoint raises a real
        DBAPIError (division by zero), which rolls back only the bonus,
        leaving the core transfer intact.
        """
        if source_account_number == destination_account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different",
            )

        try:
            # === 1. OUTER BOUNDARY: BEGIN (auto COMMIT on exit) ===
            async with session.begin():
                # --- Validate & lock accounts ---
                src_row = await session.execute(
                    text(
                        "SELECT balance, is_active FROM accounts "
                        "WHERE account_number = :acc FOR UPDATE"
                    ),
                    {"acc": source_account_number},
                )
                src_data = src_row.one_or_none()
                if not src_data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Source account '{source_account_number}' not found",
                    )
                if not src_data.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Source account '{source_account_number}' is inactive",
                    )

                dst_row = await session.execute(
                    text(
                        "SELECT balance, is_active FROM accounts "
                        "WHERE account_number = :acc FOR UPDATE"
                    ),
                    {"acc": destination_account_number},
                )
                dst_data = dst_row.one_or_none()
                if not dst_data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Destination account '{destination_account_number}' not found",
                    )
                if not dst_data.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Destination account '{destination_account_number}' is inactive",
                    )

                source_balance_before = Decimal(str(src_data.balance))
                destination_balance_before = Decimal(str(dst_data.balance))

                if source_balance_before < amount:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Insufficient balance. "
                            f"Available: {source_balance_before}, Required: {amount}"
                        ),
                    )

                # === CRITICAL: Move the money (raw SQL) ===
                await session.execute(
                    text(
                        "UPDATE accounts SET balance = balance - :amt, "
                        "version = version + 1 WHERE account_number = :acc"
                    ),
                    {"amt": amount, "acc": source_account_number},
                )
                await session.execute(
                    text(
                        "UPDATE accounts SET balance = balance + :amt, "
                        "version = version + 1 WHERE account_number = :acc"
                    ),
                    {"amt": amount, "acc": destination_account_number},
                )

                bonus_applied = False
                bonus_amt = Decimal("0.00")

                # === 2. SAVEPOINT for non-critical loyalty bonus ===
                try:
                    async with session.begin_nested():
                        # --- BEGIN SAVEPOINT (auto) ---

                        if simulate_bonus_error:
                            # Cause a real DBAPIError (division by zero)
                            await session.execute(text("SELECT 1/0"))

                        bonus_amt = (amount * Decimal("0.05")).quantize(Decimal("0.01"))
                        if bonus_amt > 0:
                            await session.execute(
                                text(
                                    "UPDATE accounts SET balance = balance + :bonus, "
                                    "version = version + 1 WHERE account_number = :acc"
                                ),
                                {
                                    "bonus": float(bonus_amt),
                                    "acc": destination_account_number,
                                },
                            )

                        # Log bonus in transactions table
                        await session.execute(
                            text(
                                """
                                INSERT INTO transactions
                                    (id, source_account, destination_account,
                                     amount, payment_type, status, created_at)
                                VALUES
                                    (:id, :src, :dst, :amt, :type, :status, NOW())
                                """
                            ),
                            {
                                "id": uuid4(),
                                "src": source_account_number,
                                "dst": destination_account_number,
                                "amt": int(bonus_amt),
                                "type": "loyalty_bonus",
                                "status": "completed",
                            },
                        )

                        bonus_applied = True
                        # --- RELEASE SAVEPOINT on success (auto) ---

                except DBAPIError:
                    # --- ROLLBACK TO SAVEPOINT (auto by begin_nested()) ---
                    # Main transaction is STILL ACTIVE.
                    # Fallback: log the failure.
                    await session.execute(
                        text(
                            """
                            INSERT INTO transactions
                                (id, source_account, destination_account,
                                 amount, payment_type, status, created_at)
                            VALUES
                                (:id, :src, :dst, 0, :type, :status, NOW())
                            """
                        ),
                        {
                            "id": uuid4(),
                            "src": source_account_number,
                            "dst": destination_account_number,
                            "type": "bonus_fallback",
                            "status": "completed",
                        },
                    )

            # === 3. COMMIT (auto on exit from session.begin()) ===

            # Re-query final balances (in a new implicit transaction)
            final_rows = await session.execute(
                text(
                    """
                    SELECT
                        (SELECT balance FROM accounts
                         WHERE account_number = :src) AS src_bal,
                        (SELECT balance FROM accounts
                         WHERE account_number = :dst) AS dst_bal
                    """
                ),
                {"src": source_account_number, "dst": destination_account_number},
            )
            final = final_rows.one()
            source_balance_after = Decimal(str(final.src_bal))
            destination_balance_after = Decimal(str(final.dst_bal))

            status_str = "completed" if bonus_applied else "bonus_rolled_back"
            message_str = (
                f"Successfully transferred {amount} from "
                f"'{source_account_number}' to '{destination_account_number}'"
                + (
                    f" and applied {bonus_amt} loyalty bonus."
                    if bonus_applied
                    else (
                        f". Bonus of {bonus_amt} failed and was rolled back "
                        f"via savepoint. Transfer preserved."
                    )
                )
            )
            savepoint_demo_str = (
                (
                    "No savepoint rollback occurred. Both transfer and bonus "
                    "were committed successfully."
                )
                if bonus_applied
                else (
                    "ROLLBACK TO SAVEPOINT executed after DBAPIError. "
                    "Bonus undone, core transfer preserved via fallback."
                )
            )

            return LoyaltyBonusResponse(
                status=status_str,
                message=message_str,
                source_account_number=source_account_number,
                destination_account_number=destination_account_number,
                amount=amount,
                source_balance_before=source_balance_before,
                source_balance_after=source_balance_after,
                destination_balance_before=destination_balance_before,
                destination_balance_after=destination_balance_after,
                loyalty_bonus_applied=bonus_applied,
                bonus_amount=bonus_amt,
                savepoint_demo=savepoint_demo_str,
            )

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transaction completely aborted due to unexpected error.",
            )
