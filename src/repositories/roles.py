from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, select, delete

from db.db import connection
from models.models import Role

class RoleRepository:
    @connection
    async def get_roles(self, session: AsyncSession) -> List[Role]:
        result = await session.execute(select(Role))
        return result.scalars().all()
    
    @connection
    async def create_role(self, data: Dict, session: AsyncSession) -> Role:
        existing_role = await session.execute(select(Role).filter(Role.name == data.model_dump()["name"]))
        if existing_role:
            raise ValueError("Такая роль уже существует в системе.")
        role = Role(**data.dict())
        session.add(role)
        await session.commit()
        return role

    @connection
    async def get_role_by_id(self, role_id: int, session: AsyncSession = None) -> Role:
        result = await session.execute(select(Role).filter(Role.id == role_id))
        return result.scalars().first()

    @connection
    async def update_role(self, role_id: int, data: Dict, session: AsyncSession = None) -> Role: 
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:  
            return None

        stmt = (
            update(Role)
            .where(Role.id == role_id)
            .values(**update_data)  
            .returning(Role)  
        )

        result = await session.execute(stmt)
        await session.commit()

        return result.scalar_one_or_none()  


    @connection
    async def delete_role(self, role_id: int, session: AsyncSession = None) -> bool:
        result = await self.get_role_by_id(role_id)

        if not result:
            return False

        await session.execute(delete(Role).where(Role.id == role_id))
        await session.commit()

        return True
