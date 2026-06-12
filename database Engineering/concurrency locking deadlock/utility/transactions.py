import asyncio
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

logger = logging.getLogger(__name__)

# A helper function/decorator to handle MVCC retries
async def run_with_retry(database: AsyncSession, transaction_coroutine, max_retries=3, backoff=0.1):
    for attempt in range(max_retries):
        try:
            # Execute the logical transaction steps
            return await transaction_coroutine(database)
        except DBAPIError as e:
            # PostgreSQL error code for serialization_failure is '40001'
            if getattr(e.orig, "pgcode", None) == "40001":
                logger.warning(f"🔄 MVCC Serialization conflict detected. Retrying {attempt + 1}/{max_retries}...")
                await database.rollback() # Reset state before retrying
                await asyncio.sleep(backoff * (2 ** attempt)) # Exponential backoff
                continue
            raise e # Reraise if it's a different DB error (e.g., syntax, constraint)
    
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="High traffic conflict. Please try again."
    )


# 1. Define the actual database work isolated from the framework endpoint
async def withdraw_logic(database: AsyncSession, account_id: int, amount: int):
    # Set the isolation level to leverage MVCC snapshot protection
    await database.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
    
    result = await database.execute(
        text("SELECT balance FROM accounts WHERE id = :id"), {"id": account_id}
    )
    balance = result.scalar_one()
    
    # Simulate a tight race condition window
    await asyncio.sleep(0.5)
    
    new_balance = balance - amount
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")
        
    await database.execute(
        text("UPDATE accounts SET balance = :balance WHERE id = :id"),
        {"balance": new_balance, "id": account_id}
    )
    await database.commit()
    return {"final_balance": new_balance}