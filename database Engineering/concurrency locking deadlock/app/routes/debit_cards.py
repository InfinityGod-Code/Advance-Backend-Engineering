import asyncio
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.account import Account, DebitCard
from app.schemas import (
    DebitCardCreate,
    DebitCardResponse,
    DebitCardTransferRequest,
    DebitCardUpdate,
    DebitSwipeRequest,
)

router = APIRouter(prefix="/debit-cards", tags=["Debit Cards"])


@router.post("/", response_model=DebitCardResponse, status_code=status.HTTP_201_CREATED)
async def create_debit_card(
    payload: DebitCardCreate, session: AsyncSession = Depends(get_session)
):
    account = await session.get(Account, payload.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    card = DebitCard(account_id=payload.account_id, type=payload.type)
    session.add(card)
    await session.commit()
    await session.refresh(card)
    return card


@router.get("/", response_model=List[DebitCardResponse])
async def list_debit_cards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(DebitCard))
    return result.scalars().all()


@router.get("/{card_id}", response_model=DebitCardResponse)
async def get_debit_card(card_id: UUID, session: AsyncSession = Depends(get_session)):
    card = await session.get(DebitCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Debit card not found")
    return card


@router.put("/{card_id}", response_model=DebitCardResponse)
async def update_debit_card(
    card_id: UUID,
    payload: DebitCardUpdate,
    session: AsyncSession = Depends(get_session),
):
    card = await session.get(DebitCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Debit card not found")

    if payload.type is not None:
        card.type = payload.type

    await session.commit()
    await session.refresh(card)
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_debit_card(
    card_id: UUID, session: AsyncSession = Depends(get_session)
):
    card = await session.get(DebitCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Debit card not found")

    await session.delete(card)
    await session.commit()


@router.post(
    "/swipe",
    status_code=status.HTTP_201_CREATED,
    description="""
        Safely debits an account via debit card using pessimistic locking (FOR UPDATE).
        Handles concurrent swipes by locking the account row, simulating an anti-fraud ML check,
        then deducting balance and recording the transaction ledger entry.
    """,
)
async def swipe_card(
    payload: DebitSwipeRequest, database: AsyncSession = Depends(get_session)
):
    async with database.begin():
        card = await database.execute(
            text(
                "SELECT id, account_id FROM debit_card WHERE card_number = :card_number FOR UPDATE"
            ),
            {"card_number": payload.card_number},
        )
        card_row = card.fetchone()
        if not card_row:
            raise HTTPException(status_code=404, detail="Card not found")

        result = await database.execute(
            text("""
                SELECT status, balance
                FROM accounts
                WHERE id = :id
                FOR UPDATE
            """),
            {"id": card_row.account_id},
        )
        account = result.fetchone()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if payload.amount > account.balance:
            raise HTTPException(
                status_code=400, detail="Card declined: Insufficient funds"
            )

        await asyncio.sleep(0.1)

        await database.execute(
            text("UPDATE accounts SET balance = balance - :amount WHERE id = :id"),
            {"amount": payload.amount, "id": card_row.account_id},
        )

        await database.execute(
            text("""
                INSERT INTO card_transactions (card_id, account_id, amount, merchant, status)
                VALUES (:card_id, :account_id, :amount, :merchant, 'APPROVED')
            """),
            {
                "card_id": card_row.id,
                "account_id": card_row.account_id,
                "amount": payload.amount,
                "merchant": payload.merchant,
            },
        )

    return {
        "status": "APPROVED",
        "amount": str(payload.amount),
        "merchant": payload.merchant,
    }


@router.post("/transfer", response_model=DebitCardResponse)
async def transfer_from_card(
    payload: DebitCardTransferRequest, session: AsyncSession = Depends(get_session)
):
    if payload.amount <= Decimal("0"):
        raise HTTPException(status_code=400, detail="Amount must be positive")

    if payload.from_card_id == payload.to_card_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same card")

    from_card = await session.get(DebitCard, payload.from_card_id)
    if not from_card:
        raise HTTPException(status_code=404, detail="Source debit card not found")

    to_card = await session.get(DebitCard, payload.to_card_id)
    if not to_card:
        raise HTTPException(status_code=404, detail="Destination debit card not found")

    id1, id2 = sorted([from_card.account_id, to_card.account_id])
    from_is_first = id1 == from_card.account_id

    stmt = (
        select(Account)
        .where(Account.id.in_([from_card.account_id, to_card.account_id]))
        .with_for_update()
    )
    result = await session.execute(stmt)
    accounts = result.scalars().all()

    if len(accounts) != 2:
        raise HTTPException(status_code=404, detail="One or both accounts not found")

    from_account = accounts[0] if from_is_first else accounts[1]
    to_account = accounts[1] if from_is_first else accounts[0]

    if from_account.balance < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    from_account.balance -= payload.amount
    to_account.balance += payload.amount

    await session.commit()
    await session.refresh(from_card)
    return from_card
