from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.m_account import AccountModel
from app.schemas.account_schema import AccountCreateRequest, AccountResponse
from uuid import UUID


class AccountService:
    """Service layer for account operations"""

    @staticmethod
    async def create_account(
        session: AsyncSession, 
        account_data: AccountCreateRequest
    ) -> AccountResponse:
        """Create a new account"""
        
        # Create new account instance
        new_account = AccountModel(
            account_number=account_data.account_number,
            owner_email=account_data.owner_email,
            balance=account_data.initial_balance
        )
        
        # Add to session and commit
        session.add(new_account)
        await session.commit()
        await session.refresh(new_account)
        
        return AccountResponse.model_validate(new_account)

    @staticmethod
    async def get_account(
        session: AsyncSession, 
        account_id: UUID
    ) -> AccountResponse | None:
        """Get account by ID"""
        
        statement = select(AccountModel).where(AccountModel.id == account_id)
        result = await session.execute(statement)
        account = result.scalar_one_or_none()
        
        if account:
            return AccountResponse.model_validate(account)
        return None

    @staticmethod
    async def get_account_by_number(
        session: AsyncSession, 
        account_number: str
    ) -> AccountModel | None:
        """Get account by account number"""
        
        statement = select(AccountModel).where(
            AccountModel.account_number == account_number
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_accounts(session: AsyncSession) -> list[AccountResponse]:
        """List all accounts"""
        
        statement = select(AccountModel).order_by(AccountModel.created_at.desc())
        result = await session.execute(statement)
        accounts = result.scalars().all()
        
        return [AccountResponse.model_validate(account) for account in accounts]

    @staticmethod
    async def update_account(
        session: AsyncSession,
        account_id: UUID,
        updates: dict
    ) -> AccountResponse | None:
        """Update an account"""
        
        statement = select(AccountModel).where(AccountModel.id == account_id)
        result = await session.execute(statement)
        account = result.scalar_one_or_none()
        
        if not account:
            return None
        
        # Update fields
        for key, value in updates.items():
            if value is not None:
                setattr(account, key, value)
        
        account.version += 1
        session.add(account)
        await session.commit()
        await session.refresh(account)
        
        return AccountResponse.model_validate(account)
