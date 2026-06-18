# app/dependancy/depandancies.py
from typing import Annotated
from fastapi import Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependancy.db import get_db
import redis.asyncio as aioredis


# Clean, decoupled dependency provider using the Request object
def get_redis_client(request: Request) -> aioredis.Redis:
    if not hasattr(request.app.state, "redis_client"):
        raise RuntimeError("Redis client is not initialized in app state")
    return request.app.state.redis_client

dbDependency = Annotated[AsyncSession, Depends(get_db)]
redisDependency = Annotated[aioredis.Redis, Depends(get_redis_client)]