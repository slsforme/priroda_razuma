from pydantic import (
    BaseModel,
    EmailStr, 
    constr,
    field_validator,
    ValidationError
)
from datetime import datetime
from typing import Optional


class Role(BaseModel):
    name: constr(min_length=3, max_length=255)
    description: Optional[str]


class User(BaseModel):
    fio: str
    created_at: datetime
    login: constr(min_length=5, max_length=50)
    password: str 
    email: EmailStr
    role: Role

    @field_validator('password')
    @classmethod
    def check_password_length(cls, value: str):
        if len(value) != 64:
            raise ValidationError('Пароль незахеширован или же технология хеширования является недопустимой.')
        return value







