from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class CardTransaction(SQLModel, table=True):
    __tablename__ = "card_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: UUID = Field(foreign_key="debit_card.id", index=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    merchant: str = Field(max_length=255)
    status: str = Field(max_length=20)
    created_at: datetime = Field(
    sa_column=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )
)
