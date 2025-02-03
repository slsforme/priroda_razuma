from abc import ABC, abstractmethod
from typing import List, Dict, TypeVar, Generic

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    def __init__(self, repository: T):
        self.repository = repository
    
    async def get_all_objects(self) -> List[T]:
        return await self.repository.get_all()

    async def create_object(self, data: Dict) -> T:
        return await self.repository.create(data)

    async def get_object_by_id(self, id: int) -> T:
        return await self.repository.get_by_id(id)

    async def update_object(self, id: int, data: Dict) -> T:
        return await self.repository.update(id, data)

    async def delete_object(self, id: int) -> bool:
        return await self.repository.delete(id)




 
