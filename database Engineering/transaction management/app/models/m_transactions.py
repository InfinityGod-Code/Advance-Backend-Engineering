from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class TransactionModel(SQLModel, table=True):
    __tablename__ = "transactions"

    # 1. Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the transaction",
    )

    # 2. Transfer Participants (stored as account numbers for business clarity)
    source_account: str = Field(
        nullable=False, description="Account number from which the amount was deducted"
    )
    destination_account: str = Field(
        nullable=False, description="Account number in which amount was credited"
    )

    # 3. Financial Details
    amount: int = Field(
        nullable=False, ge=1, description="Amount transferred (positive integer)"
    )
    payment_type: str = Field(
        default="transfer",
        nullable=True,
        description="Type of payment (e.g. transfer, refund, withdrawal)",
    )

    # 4. Status & Audit Trail
    status: str = Field(
        default="completed",
        nullable=False,
        description="Transaction status: completed / failed / rolled_back",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the transaction was created",
    )
