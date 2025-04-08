from .base import create_base_router
from schemas.roles import *
from depends import get_role_service

router = create_base_router(
    prefix="/roles",
    tags=["roles"],
    service_dependency=get_role_service,
    create_schema=RoleCreate,
    read_schema=RoleInDB,
    update_schema=RoleUpdate,
    object_name="роль",
    gender='f',
)