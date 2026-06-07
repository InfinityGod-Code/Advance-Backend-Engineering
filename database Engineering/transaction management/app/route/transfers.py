from typing import Union

from fastapi import APIRouter, HTTPException, Query, status

from app.dependancies.dependancy import sessionDB
from app.schemas.transaction_schema import (
    TransferRequest,
    TransferRollbackResponse,
    TransferSuccessResponse,
)
from app.service.transaction_service import (
    SimulatedDatabaseError,
    TransactionService,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/transfer",
    response_model=Union[TransferRollbackResponse, TransferSuccessResponse],
    status_code=status.HTTP_200_OK,
    summary="Transfer funds with toggleable error simulation",
    description=(
        "Transfers funds between two accounts.  Accepts a `simulate_error` "
        "query parameter to demonstrate ACID atomicity.\n\n"
        "**`simulate_error=true` (default):**\n"
        "Debits the source, then raises a `SimulatedDatabaseError` "
        "(mimicking a server crash) before crediting the destination.  "
        "The `except` block calls **ROLLBACK**, undoing the partial "
        "debit — atomicity is preserved.\n\n"
        "**`simulate_error=false`:**\n"
        "Completes the full transfer (debit + credit) and COMMITs.  "
        "Normal successful path."
    ),
)
async def transfer(
    transfer_data: TransferRequest,
    session: sessionDB,
    simulate_error: bool = Query(
        True,
        description=(
            "If `true`, raise a SimulatedDatabaseError mid-transfer; "
            "the except block calls ROLLBACK to demonstrate atomicity.  "
            "If `false`, complete the transfer normally (COMMIT)."
        ),
    ),
) -> Union[TransferRollbackResponse, TransferSuccessResponse]:
    """
    Transfer funds between two accounts.

    - **source_account_number**: Account to debit
    - **destination_account_number**: Account to credit
    - **amount**: Amount to transfer
    - **simulate_error** (query param, default `true`):
        - `true`  → raise SimulatedDatabaseError, caught → ROLLBACK
        - `false` → debit → credit → COMMIT

    When `simulate_error=true`, the response proves atomicity: balances
    **before** and **after** are identical.
    """
    try:
        return await TransactionService.transfer(
            session=session,
            source_account_number=transfer_data.source_account_number,
            destination_account_number=transfer_data.destination_account_number,
            amount=transfer_data.amount,
            simulate_error=simulate_error,
        )
    except HTTPException:
        raise
    except SimulatedDatabaseError:
        # This branch should never be reached since the service catches it
        # internally, but kept as a safety net for unexpected edge cases.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected database error during transfer",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer failed unexpectedly: {exc}",
        )
