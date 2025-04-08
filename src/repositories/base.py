from abc import ABC, abstractmethod
from typing import List, Dict, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from db.db import connection
from sqlalchemy.orm import sessionmaker

T = TypeVar("T")
D = TypeVar("D")


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, data: Dict, session: AsyncSession) -> T:
        """Метод для получения всех сущностей"""
        pass

    @abstractmethod
    async def update(self, data: Dict, session: AsyncSession) -> T:
        """Метод для обновления сущности"""
        pass

    @abstractmethod
    async def delete(self, id: int, session: AsyncSession) -> bool:
        """Метод удаления сущности"""
        pass

    @abstractmethod
    async def get_all(self, session: AsyncSession) -> List[T]:
        """Метод для получения всех сущностей"""
        pass

    @abstractmethod
    async def get_by_id(self, id: int, session: AsyncSession) -> T:
        """Метод для получения сущности по id"""
        pass


class BaseRepository(IRepository, Generic[D]):
    model: D

    def __init__(self, model: D):
        self.model = model

    @connection
    async def get_all(self, session: AsyncSession) -> List[D]:
        result = await session.execute(select(self.model))
        return result.scalars().all()

    @connection
    async def create(self, data: Dict, session: AsyncSession) -> D:
        if hasattr(data, "model_dump"):
            data = data.model_dump()

        model_instance = self.model(**data)
        session.add(model_instance)
        await session.commit()
        return model_instance

    @connection
    async def get_by_id(self, obj_id: int, session: AsyncSession) -> D:
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalars().first()

    @connection
    async def update(self, obj_id: int, data: Dict, session: AsyncSession) -> D:
        if hasattr(data, "model_dump"):
            data = data.model_dump()

        update_data = data

        if not update_data:
            return None

        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**update_data)
            .returning(self.model)
        )

        result = await session.execute(stmt)
        await session.commit()

        return result.scalar_one_or_none()

    @connection
    async def delete(self, obj_id: int, session: AsyncSession) -> bool:
        result = await self.get_by_id(obj_id)
        if not result:
            return False

        await session.execute(delete(self.model).where(self.model.id == obj_id))
        await session.commit()
        return True
