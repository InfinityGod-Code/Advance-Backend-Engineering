"""
Database initialization script - Creates all tables based on SQLModel definitions
Run this script to set up the database schema
"""

import asyncio
import logging
from sqlmodel import SQLModel
from app.database.database import engine
from app.models.m_account import AccountModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """Initialize database schema"""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables defined in SQLModel
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info("✓ Database schema initialized successfully!")
        logger.info(f"✓ Created table: {AccountModel.__tablename__}")
        
    except Exception as e:
        logger.error(f"✗ Error initializing database: {str(e)}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
