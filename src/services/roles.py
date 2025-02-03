from typing import List, Dict
from repositories.roles import RoleRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    async def get_roles(self):
        return await self.role_repository.get_all()

    async def create_role(self, role_data: Dict):
        return await self.role_repository.create(role_data)

    async def get_role_by_id(self, role_id: int):
        return await self.role_repository.get_by_id(role_id)

    async def update_role(self, role_id: int, data: Dict):
        return await self.role_repository.update(role_id, data)

    async def delete_role(self, role_id: int):
        return await self.role_repository.delete(role_id)
