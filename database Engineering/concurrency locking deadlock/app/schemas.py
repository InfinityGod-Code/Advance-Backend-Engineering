from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr


class AccountCreate(BaseModel):
    name: str
    email: EmailStr
    balance: Decimal = Decimal("0.00")


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class AccountResponse(BaseModel):
    id: int
    name: str
    email: str
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal


class WithdrawalCreate(BaseModel):
    account_id: int
    amount: Decimal
    name : str
    reference: Optional[str] = None


class WithdrawalResponse(BaseModel):
    id: int
    account_id: int
    amount: Decimal
    reference: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
