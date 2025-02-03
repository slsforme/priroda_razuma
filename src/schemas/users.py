from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr, field_validator, ValidationError


class UserBase(BaseModel):
    fio: constr(min_length=3, max_length=255)
    login: constr(min_length=3, max_length=50)
    role_id: int


class UserCreate(UserBase):
    password: constr(min_length=6, max_length=64)


class UserUpdate(UserBase):
    fio: Optional[constr(min_length=3, max_length=255)] = None
    login: Optional[constr(min_length=3, max_length=50)] = None
    password: Optional[constr(min_length=6, max_length=64)] = None
    role_id: Optional[int] = None


class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True
