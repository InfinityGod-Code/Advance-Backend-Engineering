import asyncio
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_session
from app.schemas import WithdrawalCreate
from utility.transactions import run_with_retry, withdraw_logic

router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])


@router.post(
    "/withdraw-unsafe",
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


@router.post(
    "/withdraw-safe",
    description="""
            Now since we impose isolation level as REPEATABLE READ its have some level of protection,
            so now if we hit two concucrrent requests at the same time one of them will finish successfully and
            the other will crash with a serialization error instead of corrupting the account balance.
    """,
)
async def create_withdrawal_repeatable(
    payload: WithdrawalCreate, database: AsyncSession = Depends(get_session)
):
    # 📋 Configure this specific transaction block to use REPEATABLE READ
    """Now we have convert this request into transaction where its consider everything as whole."""
    async with database.begin():
        # setting isolation level, we can impose other isolation here as. for reference check the notes section
        # and find the table that gives which isolation level is used for different situations. You can adapt 
        # according to your requirements needs.
        await database.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))

        # 1. Read from our snapshot
        result = await database.execute(
            text("SELECT balance FROM accounts WHERE id = :id"),
            {"id": payload.account_id},
        )
        balance = result.scalar_one()
        print(f"[{payload.name}] Read Balance: {balance}")

        await asyncio.sleep(2)  # Simulating concurrent overlap

        # 2. Try to write back
        new_balance = balance - payload.amount
        try:
            await database.execute(
                text("UPDATE accounts SET balance = :balance WHERE id = :id"),
                {"balance": new_balance, "id": payload.account_id},
            )
            print(f"[{payload.name}] Successfully updated balance to {new_balance}")
        except Exception as e:
            print(f"💥 [{payload.name}] Transaction failed! Error: {e}")
            # The database will automatically roll back here
            raise e

    return {"final_balance": new_balance}


@router.post("/withdraw-mvcc",description="""""")
async def withdraw_mvcc(payload: WithdrawalCreate, database: AsyncSession = Depends(get_session)):
    # Pass our logic block into the retry controller
    async def transaction_wrapper(session):
        return await withdraw_logic(session, payload.account_id, payload.amount)
        
    return await run_with_retry(database, transaction_wrapper)