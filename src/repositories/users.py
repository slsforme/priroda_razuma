from schemas.users import User
from typing import List
from .base import AbstractRepository



class UserRepository(AbstractRepository):
    
    async def get(self) -> List[User]:
        ...
    
    async def add(self) -> User:
        ...

    async def update(self):
        ...

    async def delete(self):
        ...

    async def get_by_id(self):
        ...

        

