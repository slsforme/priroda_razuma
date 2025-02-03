from typing import List, Dict
from repositories.users import UserRepository
from .base import BaseService


class UserService(BaseService):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
