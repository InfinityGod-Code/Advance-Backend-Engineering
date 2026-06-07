from decimal import Decimal
from uuid import UUID
from datetime import datetime
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


class TransferResponse(BaseModel):
    """
    Schema returned for a successful atomic transfer.
    Shows the updated balances of both accounts.
    """

    status: str = Field(..., description="Transaction status (completed)")
    message: str = Field(..., description="Human-readable result message")
    transaction_id: UUID = Field(
        ..., description="Unique ID of the persisted transaction record"
    )
    source_new_balance: Decimal = Field(
        ..., description="Source account balance after the transfer"
    )
    destination_new_balance: Decimal = Field(
        ..., description="Destination account balance after the transfer"
    )

    class Config:
        from_attributes = True


class TransferRollbackResponse(BaseModel):
    """
    Schema returned for the rollback demonstration endpoint.
    Proves atomicity by showing balances remain unchanged after a
    deliberately interrupted transfer.
    """

    status: str = Field(..., description="Transaction status (rolled_back)")
    message: str = Field(
        ..., description="Explanatory message about the atomicity demonstration"
    )
    source_balance_before: Decimal = Field(
        ..., description="Source account balance before the attempted transfer"
    )
    destination_balance_before: Decimal = Field(
        ..., description="Destination account balance before the attempted transfer"
    )
    source_balance_after: Decimal = Field(
        ..., description="Source account balance after rollback (should equal 'before')"
    )
    destination_balance_after: Decimal = Field(
        ...,
        description="Destination account balance after rollback (should equal 'before')",
    )
    atomicity_proven: bool = Field(
        ...,
        description="True if source and destination balances are unchanged, proving atomicity",
    )
