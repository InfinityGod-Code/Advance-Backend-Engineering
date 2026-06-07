from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel  


class AccountModel(SQLModel,table=True):
    __tablename__ = "accounts"

    # 1. Primary Key & Identification
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the account (Demonstrates Primary Key constraint)"
    )
    
    # 2. Consistency & Integrity Constraints
    account_number: str = Field(
        unique=True,
        index=True,
        nullable=False,
        description="Unique account number (Demonstrates UNIQUE and NOT NULL constraints for Consistency)"
    )
    
    owner_email: str = Field(
        nullable=False,
        description="Email of the account owner"
    )

    # 3. Financial Data (Crucial for ACID demonstration)
    # Using Decimal to prevent floating-point rounding errors
    balance: Decimal = Field(
        default=Decimal("0.00"),
        sa_column_kwargs={"server_default": "0.00"},
        description="Current available balance. Used to demonstrate Atomicity during transfers."
    )
    
    # 4. Concurrency Control (Isolation)
    version: int = Field(
        default=1,
        nullable=False,
        description="Incremented on every update. Used for Optimistic Concurrency Control (Isolation)."
    )

    # 5. Account State & Business Logic
    is_active: bool = Field(
        default=True,
        description="Inactivating an account can test application-level Consistency checks."
    )
    
    # 6. Audit Trails (Durability & Tracking)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the account was created."
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp of the last modification (Demonstrates Durability/State changes)."
    )