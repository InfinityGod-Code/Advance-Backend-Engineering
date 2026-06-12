from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.account import AccountStatus, DebitHolderType


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


class DebitCardCreate(BaseModel):
    account_id: int
    type: DebitHolderType = DebitHolderType.default


class DebitCardUpdate(BaseModel):
    type: Optional[DebitHolderType] = None


class DebitCardResponse(BaseModel):
    id: UUID
    account_id: int
    type: DebitHolderType
    card_number: str

    model_config = {"from_attributes": True}


class DebitSwipeRequest(BaseModel):
    card_number: str
    amount: Decimal
    merchant: str


class DebitCardTransferRequest(BaseModel):
    from_card_id: UUID
    to_card_id: UUID
    amount: Decimal


class WithdrawalCreate(BaseModel):
    account_id: int
    amount: Decimal
    name: str
    reference: Optional[str] = None


class WithdrawalResponse(BaseModel):
    id: int
    account_id: int
    amount: Decimal
    reference: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
