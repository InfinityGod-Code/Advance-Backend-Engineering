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


@router.post(
    "/transfer-with-loyalty",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Transfer with Loyalty Bonus using Savepoints",
    description=(
        "Transfers funds between two accounts and applies a loyalty bonus (5% of transfer amount) "
        "to the destination account. Demonstrates SQL SAVEPOINTS for partial rollback.\n\n"
        "**How Savepoints Work in This Example:**\n"
        "1. **Main Transaction Starts**: FastAPI opens a transaction\n"
        "2. **Core Transfer**: Debit source + credit destination, then SAVEPOINT 'transfer_complete'\n"
        "3. **Bonus Calculation**: Add 5% bonus to destination, then SAVEPOINT 'bonus_applied'\n"
        "4. **If Bonus Fails** (simulate_bonus_error=true):\n"
        "   - ROLLBACK TO SAVEPOINT 'transfer_complete' (undo bonus only)\n"
        "   - Transfer remains intact, outer transaction commits\n"
        "   - Result: Transfer succeeds, bonus rolled back (partial rollback)\n"
        "5. **If All Succeeds**: COMMIT the entire transaction\n\n"
        "**Key Benefit**: Savepoints allow partial rollback without losing the main transfer. "
        "This is more granular than full transaction rollback."
    ),
)
async def transfer_with_loyalty(
    transfer_data: TransferRequest,
    session: sessionDB,
    simulate_bonus_error: bool = Query(
        False,
        description=(
            "If `true`, raise an error during bonus calculation to demonstrate "
            "SAVEPOINT rollback. The transfer will succeed, but the bonus will be rolled back. "
            "If `false`, the full transfer with bonus will succeed."
        ),
    ),
):
    """
    Transfer funds with loyalty bonus using SQL savepoints.

    - **source_account_number**: Account to debit
    - **destination_account_number**: Account to credit
    - **amount**: Amount to transfer
    - **simulate_bonus_error** (query param, default `false`):
        - `true` → Simulate bonus error → ROLLBACK TO SAVEPOINT 'transfer_complete'
        - `false` → Full transfer with bonus succeeds

    **Response Scenarios:**
    1. **status: "completed"** → Transfer + bonus both succeeded
    2. **status: "bonus_rolled_back"** → Transfer succeeded, bonus was rolled back
       (demonstrates savepoint partial rollback)
    """
    try:
        return await TransactionService.transfer_with_loyalty_bonus(
            session=session,
            source_account_number=transfer_data.source_account_number,
            destination_account_number=transfer_data.destination_account_number,
            amount=transfer_data.amount,
            simulate_bonus_error=simulate_bonus_error,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer with loyalty failed: {exc}",
        )
