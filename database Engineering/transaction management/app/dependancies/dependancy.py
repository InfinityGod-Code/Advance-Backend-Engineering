from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends
from app.database.database import get_db


sessionDB = Annotated[AsyncSession,Depends(get_db)]