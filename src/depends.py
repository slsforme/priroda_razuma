from repositories.users import UserRepository
from services.users import UserService


"""
Файл внедрения зависимостей
"""

user_repository = UserRepository()

user_service = UserService(user_repository)

def get_user_service() -> UserService:
    return user_service




