from decimal import Decimal
from pydantic import BaseModel, Field


class TransferRequest(BaseModel):
    """
    Schema for initiating a fund transfer between two accounts.
    Both accounts are identified by their unique account numbers.
    """

    source_account_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Account number from which funds will be debited",
    )
    destination_account_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Account number to which funds will be credited",
    )
    amount: Decimal = Field(
        ...,
        gt=Decimal("0.00"),
        description="Amount to transfer (must be greater than 0)",
    )


class TransferSuccessResponse(BaseModel):
    """
    Returned when `simulate_error=false`.
    The full transfer (debit + credit) succeeds and is COMMITted.
    """

    status: str = Field(
        ...,
        description='Set to "completed" to indicate a successful transfer',
    )
    message: str = Field(
        ...,
        description="Human-readable success message",
    )
    source_account_number: str = Field(
        ...,
        description="Account number that was debited",
    )
    destination_account_number: str = Field(
        ...,
        description="Account number that was credited",
    )
    amount: Decimal = Field(
        ...,
        description="Amount that was transferred",
    )
    source_new_balance: Decimal = Field(
        ...,
        description="Source account balance after the transfer",
    )
    destination_new_balance: Decimal = Field(
        ...,
        description="Destination account balance after the transfer",
    )


class TransferRollbackResponse(BaseModel):
    """
    Returned when `simulate_error=true`.
    A SimulatedDatabaseError was raised mid-transfer, caught, and
    ROLLBACK was called — the database returned to its original state,
    proving ACID atomicity is preserved.
    """

    status: str = Field(
        ...,
        description=(
            'Set to "atomicity_preserved" to indicate that atomicity was maintained'
        ),
    )
    message: str = Field(
        ...,
        description="Human-readable explanation of the rollback demonstration",
    )
    source_account_number: str = Field(
        ...,
        description="Account number that was debited (then undone)",
    )
    destination_account_number: str = Field(
        ...,
        description="Account number that would have been credited",
    )
    amount: Decimal = Field(
        ...,
        description="Amount that was debited then rolled back",
    )
    source_balance_before: Decimal = Field(
        ...,
        description="Source balance at the start (before debit)",
    )
    source_balance_after: Decimal = Field(
        ...,
        description="Source balance after ROLLBACK (should equal 'before')",
    )
    destination_balance_before: Decimal = Field(
        ...,
        description="Destination balance at the start",
    )
    destination_balance_after: Decimal = Field(
        ...,
        description="Destination balance after ROLLBACK (should equal 'before')",
    )
    atomicity_proven: bool = Field(
        ...,
        description=(
            "True when both balances are unchanged, confirming atomicity "
            "was preserved by the rollback"
        ),
    )
