from datetime import datetime
from decimal import Decimal
from typing import Optional, List

import uuid

from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID
from enum import Enum


class DebitHolderType(Enum):
    default = "default"
    spouse = "spouse"
    family = "family"
    child = "child"
    other = "Other"


class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    balance: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    status: AccountStatus = Field(default=AccountStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    debit_cards: List["DebitCard"] = Relationship(back_populates="account")


class DebitCard(SQLModel, table=True):
    __tablename__ = "debit_card"
    id: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    account_id: int = Field(foreign_key="accounts.id")
    account: "Account" = Relationship(back_populates="debit_cards")
    type: DebitHolderType = Field(default=DebitHolderType.default)
    card_number: str = Field(
        default_factory=lambda: str(uuid.uuid4().int)[:16],
        max_length=16,
        unique=True,
        index=True,
    )
