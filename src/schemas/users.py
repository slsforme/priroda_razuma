from pydantic import BaseModel, EmailStr, constr, field_validator, ValidationError, validator
import bcrypt

from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    fio: constr(min_length=3, max_length=255)
    login: constr(min_length=3, max_length=50)
    role_id: int


class UserCreate(UserBase):
    password: constr(min_length=6, max_length=64)

    @validator('password')
    def hash_password(cls, password: str) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        return bcrypt.hashpw(pwd_bytes, salt)


class UserUpdate(UserBase):
    fio: Optional[constr(min_length=3, max_length=255)] = None
    login: Optional[constr(min_length=3, max_length=50)] = None
    password: Optional[constr(min_length=6, max_length=64)] = None
    role_id: Optional[int] = None


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
