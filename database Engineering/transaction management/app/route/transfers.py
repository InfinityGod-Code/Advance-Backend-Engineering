from typing import Union

from fastapi import APIRouter, HTTPException, Query, status

from app.dependancies.dependancy import sessionDB
from app.schemas.transaction_schema import (
    TransferRequest,
    TransferResponse,
    TransferRollbackResponse,
)
from app.service.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/transfer",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Atomic fund transfer (COMMIT)",
    description=(
        "Performs a complete atomic transfer from one account to another. "
        "Both accounts are locked with SELECT FOR UPDATE (pessimistic isolation) "
        "to prevent race conditions.  All changes — debit, credit, and the "
        "transaction record — are COMMITted together atomically.  If any step "
        "fails, everything is rolled back."
    ),
)
async def transfer_funds(
    transfer_data: TransferRequest,
    session: sessionDB,
) -> TransferResponse:
    """
    Execute an atomic transfer from **source_account** to **destination_account**.

    - **source_account_number**: Account to debit
    - **destination_account_number**: Account to credit
    - **amount**: Amount to transfer (> 0)

    Returns the updated balances for both accounts along with a transaction ID.
    If the source has insufficient funds or either account is inactive, a
    400/404 error is raised **before** any changes are made.
    """
    try:
        result = await TransactionService.transfer(
            session=session,
            source_account_number=transfer_data.source_account_number,
            destination_account_number=transfer_data.destination_account_number,
            amount=transfer_data.amount,
        )
        return result

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer failed unexpectedly: {exc}",
        )


@router.post(
    "/transfer-rollback",
    response_model=Union[TransferRollbackResponse, TransferResponse],
    status_code=status.HTTP_200_OK,
    summary="Atomic transfer demonstration with ROLLBACK",
    description=(
        "Demonstrates the Atomicity property of database transactions.  "
        "Accepts a `simulate_failure` query parameter that controls whether "
        "a mid-transfer failure is triggered.\n\n"
        "**`simulate_failure=true` (default):**\n"
        "Debits the source account, then **deliberately simulates "
        "a system failure** before crediting the destination.  The transaction "
        "is ROLLED BACK, proving that partial changes are never persisted — "
        "the database returns to its original consistent state.\n\n"
        "**`simulate_failure=false`:**\n"
        "Completes the full transfer (debit + credit) and COMMITs.  "
        "Use this to verify that the exact same code path produces a "
        "successful transfer when the failure flag is off."
    ),
)
async def transfer_with_rollback(
    transfer_data: TransferRequest,
    session: sessionDB,
    simulate_failure: bool = Query(
        True,
        description=(
            "If `true`, simulate a system failure mid-transfer and ROLLBACK "
            "to demonstrate atomicity.  If `false`, complete the transfer "
            "normally (COMMIT)."
        ),
    ),
) -> Union[TransferRollbackResponse, TransferResponse]:
    """
    Demonstrate ACID atomicity with a toggleable failure simulation.

    - **source_account_number**: Account that would be debited
    - **destination_account_number**: Account that would be credited
    - **amount**: Amount that would be transferred
    - **simulate_failure** (query param, default `true`):
        - `true`  → debit source, simulate failure, ROLLBACK
        - `false` → debit source, credit destination, COMMIT

    When `simulate_failure=true`, the response proves atomicity by showing
    that balances **before** and **after** are identical.
    """
    try:
        result = await TransactionService.transfer_with_rollback(
            session=session,
            source_account_number=transfer_data.source_account_number,
            destination_account_number=transfer_data.destination_account_number,
            amount=transfer_data.amount,
            simulate_failure=simulate_failure,
        )
        return result

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rollback demonstration failed unexpectedly: {exc}",
        )
