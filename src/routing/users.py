from .base import create_base_router
from schemas.users import *
from depends import get_user_service

router = create_base_router(
    prefix="/users",
    tags=["users"],
    service_dependency=get_user_service,
    create_schema=UserCreate,
    read_schema=UserInDB,
    update_schema=UserUpdate,
    object_name="пользователь",
    gender='m',
)