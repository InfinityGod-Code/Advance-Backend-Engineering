from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class Withdrawal(SQLModel, table=True):
    __tablename__ = "withdrawals"

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    reference: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    name : str = Field(default=None)
