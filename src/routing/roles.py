from typing import List, Dict
from fastapi import APIRouter, Depends, status, HTTPException

from depends import get_role_service
from services.roles import RoleService
from schemas.roles import RoleCreate, RoleInDB, RoleUpdate
from models.models import Role

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "",
    responses={400: {"description": "Bad request"}},
    response_model=List[RoleInDB],
    description="Вывод всех ролей в формате JSON.",
)
async def get_roles(
    role_service: RoleService = Depends(get_role_service),
) -> List[RoleInDB]:
    roles = await role_service.get_roles()
    if not roles:
        return None
    return roles


@router.post(
    "",
    response_model=RoleCreate,
    status_code=status.HTTP_201_CREATED,
    description="Создание новой роли.",
)
async def create_role(
    data: RoleCreate, role_service: RoleService = Depends(get_role_service)
) -> RoleCreate:
    try:
        role = await role_service.create_role(data)
        return role
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{role_id}",
    responses={400: {"description": "Bad request"}},
    response_model=RoleInDB,
    description="Вывод роли, найденной по данному id.",
)
async def get_role_by_id(
    role_id: int,
    role_service: RoleService = Depends(get_role_service),
) -> RoleInDB:
    result = await role_service.get_role_by_id(role_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Роль не была найдена."
        )
    return result


@router.put("/{role_id}", response_model=RoleUpdate, description="Обновление роли.")
async def update_role(
    role_id: int, data: RoleInDB, role_service: RoleService = Depends(get_role_service)
) -> RoleInDB:
    result = await role_service.update_role(role_id, data)
    return result


@router.delete(
    "/{role_id}",
    description="Удаление роли."
)
async def delete_role(
    role_id: int,
    role_service: RoleService = Depends(get_role_service)
) -> Dict:
    success = await role_service.delete_role(role_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Роль не была найдена."
        )
    
    return {"detail": "Роль была успешно удалена."}


