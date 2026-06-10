from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routes.accounts import router as accounts_router
from app.routes.transactions import router as transactions_router
from app.routes.withdrawals import router as withdrawals_router

app_description = """
We are focusing these topics in the project : 
Phase 2 — Concurrency Control
 - Race Conditions
 - Isolation Levels
 - Dirty Reads
 - Non-Repeatable Reads
 - Phantom Reads
Phase 3 — Locking Strategies
 - Row-Level Locking
 - Table-Level Locking
 - Optimistic Locking
 - Pessimistic Locking
 - SELECT FOR UPDATE
Phase 4 — Deadlock Management
 - Deadlock Detection
 - Deadlock Prevention
 - Lock Ordering
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(description=app_description, lifespan=lifespan)

app.include_router(accounts_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(withdrawals_router, prefix="/api/v1")


@app.get("/")
def run():
    return {"content": "Hello from the content!"}
