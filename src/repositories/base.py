from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Dict
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


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
