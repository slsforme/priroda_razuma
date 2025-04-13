from pydantic import BaseModel, validator
import bcrypt

class BaseUser(BaseModel):
    login: str
    password: str
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user_id: int

class UserLogin(BaseUser):
    pass

class UserRegister(BaseUser):
    fio: str
    role_id: int
    
    @validator('password')
    def hash_password(cls, password: str) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        return bcrypt.hashpw(pwd_bytes, salt)