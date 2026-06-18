# main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
import redis.asyncio as aioRedis
from app.database.session import engine
from app.routes.product import router as product_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # 1. Initialize Redis client locally inside lifespan
        redis_client = aioRedis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
        )
        
        # 2. Attach it to FastAPI's state system
        app.state.redis_client = redis_client
        
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # 3. Clean teardown
    await app.state.redis_client.close()
    await engine.dispose()

app_description = "..."
app = FastAPI(title="Performance Optimizations", description=app_description, lifespan=lifespan)
app.include_router(product_router, prefix="/api/v1")

@app.get("/")
def test():
    return {"content": "hello world"}