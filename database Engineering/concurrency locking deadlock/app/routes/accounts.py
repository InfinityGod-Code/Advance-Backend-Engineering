from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.account import Account
from app.schemas import AccountCreate, AccountResponse, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate, session: AsyncSession = Depends(get_session)
):
    existing = await session.execute(select(Account).where(Account.email == payload.email))
    if existing.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    account = Account(name=payload.name, email=payload.email, balance=payload.balance)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Account))
    return result.scalars().all()


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, session: AsyncSession = Depends(get_session)):
    account = await session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    payload: AccountUpdate,
    session: AsyncSession = Depends(get_session),
):
    account = await session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if payload.name is not None:
        account.name = payload.name
    if payload.email is not None:
        existing = await session.execute(
            select(Account).where(
                Account.email == payload.email, Account.id != account_id
            )
        )
        if existing.first():
            raise HTTPException(status_code=400, detail="Email already in use")
        account.email = payload.email

    await session.commit()
    await session.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, session: AsyncSession = Depends(get_session)):
    account = await session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    await session.delete(account)
    await session.commit()
