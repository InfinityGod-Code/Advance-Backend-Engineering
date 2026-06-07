from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime
from uuid import UUID


class AccountCreateRequest(BaseModel):
    """Schema for creating a new account"""
    account_number: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Unique account number"
    )
    owner_email: EmailStr = Field(
        ...,
        description="Email of the account owner"
    )
    initial_balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        description="Initial balance for the account"
    )


class AccountResponse(BaseModel):
    """Schema for account response"""
    id: UUID
    account_number: str
    owner_email: str
    balance: Decimal
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountUpdateRequest(BaseModel):
    """Schema for updating account"""
    owner_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
