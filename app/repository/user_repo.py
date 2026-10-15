from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    async def get_user_by_email(self, session: AsyncSession, email: str):
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalars().first()
