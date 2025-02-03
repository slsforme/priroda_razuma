from repositories.users import UserRepository
from repositories.roles import RoleRepository
from services.users import UserService
from services.roles import RoleService


"""
Файл внедрения зависимостей
"""

user_repository = UserRepository()
role_repository = RoleRepository()

user_service = UserService(user_repository)
role_service = RoleService(role_repository)


def get_user_service() -> UserService:
    return user_service


def get_role_service() -> RoleService:
    return role_service
