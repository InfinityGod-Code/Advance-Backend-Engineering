from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.config import database_settings
from typing import AsyncGenerator


# 1. Create the engine (Manages the pool)
engine = create_async_engine(
    url=database_settings.POSTGRES_URL,
    echo=True,  # Set to False in production!
    pool_size=10,          # Best practice optimization
    max_overflow=20,       # Best practice optimization
)

# 2. Create the Session Factory
# expire_on_commit=False prevents SQLAlchemy from expiring objects after you commit a transaction,
# which is essential for async applications where data might be read later.
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. The FastAPI Dependency (Yields a session per request)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def create_db_tables():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)