from typing import List
from fastapi import APIRouter, Depends

from depends import get_user_service
from schemas.users import User
from services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    responses={400: {"description": "Bad request"}},
    response_model=List[User],
    description="Вывод всех пользователей",
)
async def get_users(
    user_service: UserService = Depends(get_user_service),
) -> List[User]:
    users = user_service.get_users()
    return users
