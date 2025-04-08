from repositories.users import UserRepository
from .base import BaseService
from models.models import User

class UserService(BaseService):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def get_object_by_login(self, login: str) -> User:
        return await self.repository.get_by_name(login)
