from typing import List, Dict
from fastapi import APIRouter, Depends, status

from depends import get_user_service
from schemas.users import UserCreate, UserInDB, UserUpdate
from services.users import UserService
from models.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    responses={400: {"description": "Bad request"}},
    response_model=List[UserInDB],
    description="Вывод всех пользователей в формате JSON.",
)
async def get_users(
    user_service: UserService = Depends(get_user_service),
) -> List[UserInDB]:
    users = await user_service.get_all_objects()
    if not users:
        return None
    return users


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserCreate,
    description="Создание пользователя.",
)
async def create_user(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.create_object(data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{user_id}",
    responses={400: {"description": "Bad request"}},
    response_model=UserInDB,
    description="Вывод пользователя, найденной по данному id.",
)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> UserInDB:
    result = await user_service.get_object_by_id(user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не был найден."
        )
    return result


@router.put(
    "/{user_id}",
    response_model=UserUpdate,
    description="Обновление данных пользователя.",
)
async def update_user(
    user_id: int, data: UserInDB, user_service: UserService = Depends(get_user_service)
) -> UserInDB:
    result = await user_service.update_object(user_id, data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не был найден."
        )

    return result


@router.delete("/{user_id}", description="Удаление пользователя.")
async def delete_user(
    user_id: int, user_service: UserService = Depends(get_user_service)
) -> Dict:
    success = await user_service.delete_object(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не был найден."
        )

    return {"detail": "Пользователь была успешно удалён."}
