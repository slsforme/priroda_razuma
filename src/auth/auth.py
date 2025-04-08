import jwt
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta

from depends import get_user_service, get_role_service
from services.users import UserService
from services.roles import RoleService
from .utils import validate_password, encode_jwt, decode_jwt, hash_password
from models.models import User
from .schema import *

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service) 
    ) -> User:
    try:
        payload = decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_service.get_object_by_login(payload.get("sub"))

    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or deleted",
        )
    return user

@router.post("/register", status_code=201)
async def register(
    user_data: UserRegister,
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service)
    ):
    if await user_service.get_object_by_login(user_data.login):
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким логином уже существует",
        )

    if not await role_service.get_object_by_id(user_data.role_id):
        raise HTTPException(
            status_code=404,
            detail="Данной Роли не существует",
        )

    user = await user_service.create_object(user_data)
    return user.id    
    
    user = await User.create(
        **user_data.dict(exclude={"password"}),
        password=hashed_password,
    )

    return {"id": user.id}

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_object_by_login(form_data.username)
    
    if not user or not validate_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )   
    
    access_token_data = {
        "sub": user.login,
        "user_id": user.id,
        "role_id": user.role_id,
        "type": "access",
    }

    refresh_token_data = {
        "sub": user.login,
        "type": "refresh",
    }

    access_token = encode_jwt(access_token_data)
    refresh_token = encode_jwt(refresh_token_data, expire_timedelta=timedelta(days=7))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Form(...),
    user_service: UserService = Depends(get_user_service)
):
    try:
        payload = decode_jwt(refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_service.get_object_by_login(payload.get("sub"))
    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_data = {
        "sub": user.login,
        "user_id": user.id,
        "role_id": user.role_id,
        "type": "access",
    }
    new_access_token = encode_jwt(access_token_data, expire_timedelta=timedelta(minutes=15))

    new_refresh_token = encode_jwt(
        {"sub": user.login, "type": "refresh"}, 
        expire_timedelta=timedelta(days=7)
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "Bearer",
    }


"""
def require_role(role_id: int):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role_id < role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return role_checker

# usage
@app.get("/admin/dashboard")
async def admin_dashboard(user: User = Depends(require_role(ADMIN_ROLE_ID))):
    return {"message": "Admin dashboard"}
"""

