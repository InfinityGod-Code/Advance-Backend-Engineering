from decimal import Decimal
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.m_account import AccountModel
from app.models.m_transactions import TransactionModel
from app.schemas.transaction_schema import TransferResponse, TransferRollbackResponse


class TransactionService:
    """
    Service layer for transfer operations.
    Demonstrates ACID atomicity via commit and rollback scenarios.
    Uses `select_for_update` (pessimistic locking) to ensure Isolation
    even during concurrent transfers.
    """

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _get_account_locked(
        session: AsyncSession, account_number: str
    ) -> AccountModel:
        """
        Fetch an account by number with a row-level lock (FOR UPDATE).
        This prevents concurrent transactions from modifying the same row
        until our transaction completes (commit or rollback).
        """
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
        """
        Lock both accounts in a **consistent order** (by account number)
        to prevent deadlocks when multiple transfers run concurrently.
        Returns (source_account, destination_account).
        """
        # Always lock the lexicographically smaller account number first
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

    # ------------------------------------------------------------------
    # 1.  COMMIT — Full atomic transfer with no rollback
    # ------------------------------------------------------------------

    @staticmethod
    async def transfer(
        session: AsyncSession,
        source_account_number: str,
        destination_account_number: str,
        amount: Decimal,
    ) -> TransferResponse:
        """
        Perform an atomic transfer inside a single database transaction.
        Either ALL steps succeed (COMMIT) or NONE are persisted.
        Steps:
          1. Lock both accounts (pessimistic isolation).
          2. Validate source has sufficient balance.
          3. Debit source, credit destination.
          4. Persist a TransactionModel record.
          5. COMMIT — all changes become durable.
        """
        if source_account_number == destination_account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different",
            )

        source, destination = await TransactionService._lock_accounts_in_order(
            session, source_account_number, destination_account_number
        )

        # Validate balance
        if source.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance in source account "
                f"'{source_account_number}'. "
                f"Available: {source.balance}, Required: {amount}",
            )

        # Apply the transfer
        source.balance -= amount
        destination.balance += amount
        source.version += 1
        destination.version += 1

        # Create a transaction record
        txn_record = TransactionModel(
            source_account=source_account_number,
            destination_account=destination_account_number,
            amount=int(amount),  # stored as integer (cents / smallest unit)
            payment_type="transfer",
            status="completed",
        )
        session.add(source)
        session.add(destination)
        session.add(txn_record)

        # Commit everything atomically — if this fails, ALL changes roll back
        await session.commit()

        # Refresh to get the latest DB-generated values
        await session.refresh(source)
        await session.refresh(destination)

        return TransferResponse(
            status="completed",
            message=f"Successfully transferred {amount} from "
            f"{source_account_number} to {destination_account_number}.",
            transaction_id=txn_record.id,
            source_new_balance=source.balance,
            destination_new_balance=destination.balance,
        )

    # ------------------------------------------------------------------
    # 2.  ROLLBACK — Demonstrates atomicity by interrupting the transfer
    # ------------------------------------------------------------------

    @staticmethod
    async def transfer_with_rollback(
        session: AsyncSession,
        source_account_number: str,
        destination_account_number: str,
        amount: Decimal,
        simulate_failure: bool = True,
    ) -> TransferResponse | TransferRollbackResponse:
        """
        Transfer endpoint with a toggleable failure simulation.

        When `simulate_failure=True` (default):
          Debit source → simulate system failure → ROLLBACK.
          Proves atomicity: balances are unchanged.

        When `simulate_failure=False`:
          Debit source → credit destination → COMMIT.
          Acts as a normal atomic transfer.

        Both paths share the same validation and initial debit,
        making the atomicity comparison immediately clear.
        """
        if source_account_number == destination_account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different",
            )

        # 1. Capture initial balances for the rollback comparison
        source_orig = await TransactionService._get_account_locked(
            session, source_account_number
        )
        dest_orig = await TransactionService._get_account_locked(
            session, destination_account_number
        )
        source_balance_before = source_orig.balance
        destination_balance_before = dest_orig.balance

        # Validate balance
        if source_balance_before < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance in source account "
                f"'{source_account_number}'. "
                f"Available: {source_balance_before}, Required: {amount}",
            )

        # 2. Lock accounts in consistent order and debit the source
        source, destination = await TransactionService._lock_accounts_in_order(
            session, source_account_number, destination_account_number
        )

        source.balance -= amount
        source.version += 1
        session.add(source)

        # 3. Branch on simulate_failure
        if simulate_failure:
            # --- ROLLBACK PATH: simulate failure before crediting destination ---

            txn_record = TransactionModel(
                source_account=source_account_number,
                destination_account=destination_account_number,
                amount=int(amount),
                payment_type="transfer",
                status="failed",
            )
            session.add(txn_record)

            await session.flush()  # Push changes so the DB sees them

            # Simulated failure
            await session.rollback()

            # Re-query accounts to confirm they are back to original balances
            source_after_stmt = select(AccountModel).where(
                AccountModel.account_number == source_account_number
            )
            dest_after_stmt = select(AccountModel).where(
                AccountModel.account_number == destination_account_number
            )
            source_after = (await session.execute(source_after_stmt)).scalar_one()
            dest_after = (await session.execute(dest_after_stmt)).scalar_one()

            return TransferRollbackResponse(
                status="rolled_back",
                message=(
                    "Simulated system failure: transaction interrupted after debiting "
                    "source but before crediting destination.  "
                    "Rollback ensured no partial changes were persisted."
                ),
                source_balance_before=source_balance_before,
                destination_balance_before=destination_balance_before,
                source_balance_after=source_after.balance,
                destination_balance_after=dest_after.balance,
                atomicity_proven=(
                    source_after.balance == source_balance_before
                    and dest_after.balance == destination_balance_before
                ),
            )
        else:
            # --- COMMIT PATH: complete the transfer successfully ---

            destination.balance += amount
            destination.version += 1

            txn_record = TransactionModel(
                source_account=source_account_number,
                destination_account=destination_account_number,
                amount=int(amount),
                payment_type="transfer",
                status="completed",
            )
            session.add(source)
            session.add(destination)
            session.add(txn_record)

            await session.commit()
            await session.refresh(source)
            await session.refresh(destination)

            return TransferResponse(
                status="completed",
                message=f"Successfully transferred {amount} from "
                f"{source_account_number} to {destination_account_number}.",
                transaction_id=txn_record.id,
                source_new_balance=source.balance,
                destination_new_balance=destination.balance,
            )
