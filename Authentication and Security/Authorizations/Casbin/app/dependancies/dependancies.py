from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends
from app.database import get_db

sessionDB = Annotated[AsyncSession,Depends(get_db)]