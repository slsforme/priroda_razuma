from schemas.users import User
from typing import List

class UserRepository:
    
    def get_users(self) -> List[User]:
        ...
    
    def create_user(self) -> User:
        ...

