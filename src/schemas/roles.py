from typing import Optional
from pydantic import BaseModel, constr


class RoleBase(BaseModel):
    name: constr(min_length=3, max_length=255)
    description: Optional[constr(max_length=1000)] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    name: Optional[constr(min_length=3, max_length=255)]
    description: Optional[constr(max_length=1000)] = None


class RoleInDB(RoleBase):
    id: int

    class Config:
        from_attributes = True
