from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.schemas import AccountResponse, TransferRequest

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/withdraw", response_model=AccountResponse)
async def transfer(
    payload: TransferRequest, database: AsyncSession = Depends(get_session)
):
    pass
