from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.database.database import create_db_tables
from app.route.accounts import router as account_router
from app.route.transfers import router as transfer_router

description = """
**FastAPI Transaction Management Demo**
A FastAPI-based project designed to demonstrate core database transaction concepts using practical,
real-world examples. The project covers ACID properties, transaction lifecycle management,
commit and rollback operations, and savepoints through interactive APIs.
It helps developers understand how databases maintain consistency, handle failures,
and ensure reliable data processing in production systems.
Perfect for learning transaction management, database internals, and backend engineering fundamentals using FastAPI and PostgreSQL.
"""


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(
    title="Transaction Management", description=description, lifespan=lifespan_handler
)

app.include_router(account_router)
app.include_router(transfer_router)


@app.get("/")
def main():
    return {"content": "Hello world"}
