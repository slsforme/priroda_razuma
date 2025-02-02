from typing import List
from repositories.users import UserRepository
from schemas.users import User

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_users(self) -> List[User]:
        users = self.repository.get_users()
        return users 
    
    def create_user(self) -> User:
        result = self.repository.create_user()
        return result 