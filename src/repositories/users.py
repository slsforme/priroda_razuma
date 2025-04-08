from models.models import User
from .base import BaseRepository
from db.db import connection
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    @connection
    async def get_by_name(self, login: str, session: AsyncSession) -> User:
        result = await session.execute(
            select(User).where(User.login == login)
        )
        return result.scalars().first()
