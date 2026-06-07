

from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from app.dependancies.dependancy import sessionDB
from app.schemas.account_schema import (
    AccountCreateRequest, 
    AccountResponse,
    AccountUpdateRequest
)
from app.service.account_service import AccountService


router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "/", 
    response_model=AccountResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Creates a new account with the provided details"
)
async def create_account(
    account_data: AccountCreateRequest, 
    session: sessionDB
) -> AccountResponse:
    """
    Create a new account with:
    - **account_number**: Unique identifier for the account
    - **owner_email**: Email of the account owner
    - **initial_balance**: Starting balance (optional, defaults to 0.00)
    """
    try:
        # Check if account number already exists
        existing_account = await AccountService.get_account_by_number(
            session, 
            account_data.account_number
        )
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Account with number {account_data.account_number} already exists"
            )
        
        account = await AccountService.create_account(session, account_data)
        return account
    
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating account: {str(e)}"
        )


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get account by ID",
    description="Retrieves a specific account by its ID"
)
async def get_account(
    account_id: UUID, 
    session: sessionDB
) -> AccountResponse:
    """Get account details by ID"""
    account = await AccountService.get_account(session, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    return account


@router.get(
    "/",
    response_model=list[AccountResponse],
    summary="List all accounts",
    description="Retrieves all accounts"
)
async def list_accounts(session: sessionDB) -> list[AccountResponse]:
    """Get list of all accounts"""
    accounts = await AccountService.list_accounts(session)
    return accounts


@router.patch(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update account",
    description="Updates account details"
)
async def update_account(
    account_id: UUID,
    account_data: AccountUpdateRequest,
    session: sessionDB
) -> AccountResponse:
    """Update account information"""
    account = await AccountService.update_account(
        session,
        account_id,
        account_data.model_dump(exclude_unset=True)
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    return account