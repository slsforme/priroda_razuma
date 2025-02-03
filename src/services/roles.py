from typing import List, Dict
from repositories.roles import RoleRepository
from .base import BaseService


class RoleService(BaseService):
    def __init__(self, repository: RoleRepository):
        super().__init__(repository)
