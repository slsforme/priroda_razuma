from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, select

from db.db import connection
from models.models import User


class UserRepository:
    @connection
    async def get_users(self, session: AsyncSession) -> List[User]:
        result = await session.execute(select(User))
        return result.scalars().all()

    @connection
    async def create_user(self, data: Dict, session: AsyncSession) -> User:
        existing_user = await session.execute(select(User).filter(User.fio == data.model_dump()["fio"]))
        if existing_user:
            raise ValueError("Пользователь с таким ФИО уже существует в системе.")
        user = User(**data.dict())
        session.add(user)
        await session.commit()
        return user

    @connection
    async def get_user_by_id(self, user_id: int, session: AsyncSession = None) -> User:
        result = await session.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    @connection
    async def update_user(
        self, user_id: int, data: Dict, session: AsyncSession = None
    ) -> User:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return None

        stmt = (
            update(User).where(User.id == user_id).values(**update_data).returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()

        return result.scalar_one_or_none()

    @connection
    async def delete_user(self, user_id: int, sessions: AsyncSession = None) -> bool:
        result = await self.get_user_by_id(user_id)
        user = result.scalar_one_or_none()

        if not user:
            return False

        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()

        return True

