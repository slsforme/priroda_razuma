from typing import List, Dict, Any, TypeVar, Generic, Type, Optional
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Form, Response
from pydantic import BaseModel, ValidationError
from redis import asyncio as aioredis
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from urllib.parse import quote
import json
import traceback
from services.base import BaseService
from config import settings, logger
from cache.utils import Base64Coder
from .utils import get_russian_forms

T = TypeVar('T', bound=BaseModel)  
DB = TypeVar('DB', bound=BaseModel)  
U = TypeVar('U', bound=BaseModel)  

def create_base_router(
    prefix: str,
    tags: List[str],
    service_dependency,
    create_schema: Type[T],
    read_schema: Type[DB],
    update_schema: Type[U],
    object_name: str = "объект",
    gender: str = 'm',
    has_file_field: bool = False,
    file_field_name: str = "data"
):
    forms = get_russian_forms(object_name, gender)
    router = APIRouter(prefix=prefix, tags=tags)
    cache_prefix = prefix.strip("/")
    
    def custom_key_builder(func, namespace: Optional[str] = None, *args, **kwargs):
        namespace = namespace or f"{cache_prefix}"
        prefix = f"{FastAPICache.get_prefix()}:fastapi_cache:{namespace}:"
        module_path = func.__module__
        function_name = func.__qualname__
        if function_name == "get_all":
            cache_key = f"{prefix}:{module_path}:{function_name}"
        else:
            cache_key = f"{prefix}:{module_path}:{function_name}"
            arg_dict = kwargs
            if args:
                func_args = func.__code__.co_varnames
                for i, arg_name in enumerate(func_args[1:]):  
                    if i < len(args):
                        arg_dict[arg_name] = args[i]
            for key, value in arg_dict.items():
                if key not in ["service", "session"]:
                    cache_key += f":{key}:{str(value)}"
        return cache_key.replace(" ", "_")

    @router.get(
        "",
        responses={
            200: {"description": f"Successfully retrieved list of {forms['genitive_plural']}"},
            500: {"description": "Internal server error"}
        },
        response_model=List[read_schema],
        description=f"Получение списка всех {forms['genitive_plural']} в формате JSON.",
    )
    async def get_all(service: BaseService = Depends(service_dependency)) -> List[read_schema]:
        try:
            objects = await service.get_all_objects()
            return objects if objects else []
        except Exception as e:
            logger.error(f"Get all error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve {forms['genitive_plural']}"
            )

    if has_file_field:
        @router.post(
            "",
            response_model=read_schema,
            status_code=status.HTTP_201_CREATED,
            responses={
                201: {"description": f"{forms['именительный'].capitalize()} успешно создан"},
                400: {"description": "Invalid request data"},
                422: {"description": "Validation error"},
                500: {"description": "Internal server error"}
            },
            description=f"Создание нового {forms['родительный']} с файлом.",
        )
        async def create(file: UploadFile = File(...), data: str = Form(...), service = Depends(service_dependency)) -> read_schema:
            try:
                data_dict = json.loads(data)
                file_content = await file.read()
                data_dict[file_field_name] = file_content
                try:
                    validated_data = create_schema(**data_dict)
                except ValidationError as e:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
                result = await service.create_object(validated_data)
                return result
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Create error: {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create {forms['родительный']}")
    else:
        @router.post(
            "",
            response_model=read_schema,
            status_code=status.HTTP_201_CREATED,
            responses={
                201: {"description": f"{forms['именительный'].capitalize()} успешно создан"},
                400: {"description": "Invalid request data"},
                422: {"description": "Validation error"},
                500: {"description": "Internal server error"}
            },
            description=f"Создание нового {forms['родительный']}.",
        )
        async def create(data: create_schema, service = Depends(service_dependency)) -> read_schema:
            try:
                obj = await service.create_object(data)
                await invalidate_cache()
                return obj
            except ValueError as e:
                logger.error(f"Validation error: {str(e)}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            except Exception as e:
                logger.error(f"Create error: {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create {forms['родительный']}")

    @router.get(
        "/{obj_id}",
        responses={
            200: {"description": f"{forms['именительный'].capitalize()} успешно получен"},
            404: {"description": f"{forms['именительный'].capitalize()} не {forms['найден']}"},
            500: {"description": "Internal server error"}
        },
        response_model=read_schema,
        description=f"Получение {forms['родительный']} по идентификатору.",
    )
    @cache(expire=settings.cache_ttl, coder=Base64Coder, key_builder=custom_key_builder)
    async def get_by_id(obj_id: int, service: BaseService = Depends(service_dependency)) -> read_schema:
        try:
            result = await service.get_object_by_id(obj_id)
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{forms['именительный'].capitalize()} не {forms['найден']}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get by ID error: {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve {forms['родительный']}")

    if has_file_field:
        @router.put(
            "/{obj_id}", 
            response_model=read_schema,
            responses={
                200: {"description": f"{forms['именительный'].capitalize()} успешно обновлен"},
                400: {"description": "Invalid request data"},
                404: {"description": f"{forms['именительный'].capitalize()} не {forms['найден']}"},
                422: {"description": "Validation error"},
                500: {"description": "Internal server error"}
            },
            description=f"Обновление {forms['родительный']} с файлом."
        )
        async def update(obj_id: int, file: Optional[UploadFile] = File(None), data: Optional[str] = Form(None), service = Depends(service_dependency)) -> read_schema:
            try:
                existing_obj = await service.get_object_by_id(obj_id)
                if not existing_obj:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{forms['именительный'].capitalize()} не {forms['найден']}")
                data_dict = {}
                if data:
                    try:
                        data_dict = json.loads(data)
                    except json.JSONDecodeError:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format")
                if file and file.filename:
                    file_content = await file.read()
                    data_dict[file_field_name] = file_content
                try:
                    update_data = update_schema(**data_dict).dict(exclude_unset=True)
                except ValidationError as e:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
                result = await service.update_object(obj_id, update_data)
                return result
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Update error: {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update {forms['родительный']}")
    else:
        @router.put(
            "/{obj_id}", 
            response_model=read_schema,
            responses={
                200: {"description": f"{forms['именительный'].capitalize()} успешно обновлен"},
                400: {"description": "Invalid request data"},
                404: {"description": f"{forms['именительный'].capitalize()} не {forms['найден']}"},
                422: {"description": "Validation error"},
                500: {"description": "Internal server error"}
            },
            description=f"Обновление {forms['родительный']}."
        )
        async def update(obj_id: int, data: update_schema, service = Depends(service_dependency)) -> read_schema:
            try:
                update_data = data.dict(exclude_unset=True)
                result = await service.update_object(obj_id, update_data)
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{forms['именительный'].capitalize()} не {forms['найден']}")
                return result
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Update error: {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update {forms['родительный']}")

    @router.delete(
        "/{obj_id}", 
        responses={
            200: {"description": f"{forms['именительный'].capitalize()} успешно {forms['удален']}"},
            404: {"description": f"{forms['именительный'].capitalize()} не {forms['найден']}"},
            500: {"description": "Internal server error"}
        },
        description=f"Удаление {forms['родительный']}.",
    )
    async def delete(obj_id: int, service = Depends(service_dependency)) -> Dict:
        try:
            success = await service.delete_object(obj_id)
            if not success:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{forms['именительный'].capitalize()} не {forms['найден']}")
            return {"detail": f"{forms['именительный'].capitalize()} успешно {forms['удален']}"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete error: {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete {forms['родительный']}")

    if has_file_field:
        @router.get(
            "/{obj_id}/download",
            responses={
                200: {"description": "File downloaded successfully"},
                404: {"description": f"{forms['именительный'].capitalize()} не {forms['найден']}"},
                500: {"description": "Internal server error"}
            },
            description=f"Скачивание файла {forms['родительный']}.",
            response_class=Response
        )
        @cache(expire=settings.cache_ttl, coder=Base64Coder, key_builder=custom_key_builder)
        async def download_file(obj_id: int, service = Depends(service_dependency)):
            try:
                result = await service.get_object_by_id(obj_id)
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{forms['именительный'].capitalize()} не {forms['найден']}")
                file_data = getattr(result, file_field_name)
                file_name = getattr(result, "name", f"{object_name}_{obj_id}")
                encoded_file_name = quote(file_name)
                return Response(
                    content=file_data,
                    headers={
                        "Content-Disposition": f"attachment; filename={encoded_file_name}",
                        "Content-Type": "application/octet-stream"
                    }
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Download error: {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download file")

    return router