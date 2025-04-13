from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from redis.exceptions import RedisError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from routing.users import router as user_routing
from routing.roles import router as role_routing
from routing.patients import router as patients_routing
from routing.documents import router as documents_routing
from auth.auth import router as auth_router, get_current_user
from routing.analitics import router as analitics_routing
from config import settings

app = FastAPI(
    docs_url=f"{settings.api_v1_prefix}/docs",
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

protected_router = APIRouter(
    prefix=settings.api_v1_prefix,
    dependencies=[Depends(get_current_user)],
)

protected_router.include_router(user_routing)
protected_router.include_router(role_routing)
protected_router.include_router(patients_routing)
protected_router.include_router(documents_routing)
protected_router.include_router(analitics_routing)

app.include_router(protected_router)

app.include_router(auth_router, prefix=settings.api_v1_prefix)

@app.on_event("startup")
async def startup():
   redis = aioredis.from_url(settings.redis_url, encoding="utf8", decode_responses=True)
   FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

