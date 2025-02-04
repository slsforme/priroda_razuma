from models.models import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
