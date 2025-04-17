from fastapi import FastAPI, Depends, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette_prometheus import PrometheusMiddleware
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
import time
from typing import AsyncGenerator
from routing.users import router as user_routing
from routing.roles import router as role_routing
from routing.patients import router as patients_routing
from routing.documents import router as documents_routing
from auth.auth import router as auth_router, get_current_user
from routing.analitics import router as analitics_routing
from config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from metrics.metrics import REQUEST_COUNT, HTTP_ERRORS, API_RESPONSE_TIME, get_metrics
from tasks.tasks import start_metrics_task

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis = aioredis.from_url(settings.redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    start_metrics_task()
    yield
    await FastAPICache.clear()

app = FastAPI(
    lifespan=lifespan,
    docs_url=f"{settings.api_v1_prefix}/docs",
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", get_metrics)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path.rstrip('/')
    status_code = 500
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        status_code = 500
        raise e
    finally:
        duration = time.time() - start_time
        
        API_RESPONSE_TIME.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).observe(duration)
        
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        if 400 <= status_code < 600:
            HTTP_ERRORS.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

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