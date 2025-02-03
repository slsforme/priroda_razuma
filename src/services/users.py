from typing import List, Dict
from repositories.users import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_users(self):
        return await self.user_repository.get_all()

    async def create_user(self, user_data: Dict):
        return await self.user_repository.create(user_data)

    async def get_user_by_id(self, user_id: int):
        return await self.user_repository.get_by_id(user_id)

    async def update_user(self, user_id: int, data: Dict):
        return await self.user_repository.update(user_id, data)

    async def delete_user(self, user_id: int):
        return await self.user_repository.delete(user_id)
