import asyncio
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_session
from app.schemas import WithdrawalCreate

router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])


@router.post(
    "/demo-concurrency",
    status_code=status.HTTP_201_CREATED,
    description="""This end-point will be used for the demonstration purpose when two concurent requests are 
    made you can see that one requests overrides the other process in the database when makes the inconsistent
    data.
    """,
)
async def create_withdrawal(
    payload: WithdrawalCreate, database: AsyncSession = Depends(get_session)
):
    result = await database.execute(
        text("SELECT balance FROM accounts WHERE id = :id"), {"id": payload.account_id}
    )
    balance = result.scalar_one()
    print(f"[{payload.name}] Read Balance: {balance}")
    await asyncio.sleep(2)
    new_balance = balance - payload.amount

    await database.execute(
        text("""
            UPDATE accounts
            SET balance = :balance
            WHERE id = :id
            """),
        {
            "balance": new_balance,
            "id": payload.account_id,
        },
    )

    await database.commit()
    print(f"[{payload.name}] Wrote New Balance: {new_balance}")
    return {"final_balance": new_balance}
