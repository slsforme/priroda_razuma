from models.models import Role
from .base import BaseRepository


class RoleRepository(BaseRepository):
    def __init__(self):
        super().__init__(Role)
