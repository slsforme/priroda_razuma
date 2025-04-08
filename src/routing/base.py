from typing import List, Dict, Any, TypeVar, Generic, Type, Optional
from fastapi import ( 
    APIRouter,
    Depends, 
    status, 
    HTTPException, 
    File, 
    UploadFile, 
    Form, 
    Response 
)
from pydantic import BaseModel
from redis import asyncio as aioredis
from fastapi_cache.decorator import cache

from urllib.parse import quote
import json
import base64

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
    cache_prefix = prefix[:-1]
    
    @router.get(
        "",
        responses={400: {"description": "Неверный запрос"}},
        response_model=List[read_schema],
        description=f"Получение списка всех {forms['genitive_plural']} в формате JSON.",
    )
    @cache(expire=settings.cache_ttl, coder=Base64Coder)
    async def get_all(
        service: BaseService = Depends(service_dependency),
    ) -> List[read_schema]:        
        objects = await service.get_all_objects()
        return objects if objects else []
    
    if has_file_field:
        @router.put(
            "/{obj_id}", 
            response_model=read_schema, 
            description=f"Обновление {forms['родительный']} с файлом."
        )
        async def update(
            obj_id: int,
            file: Optional[UploadFile] = File(None),
            form_data: str = Form(...),
            service = Depends(service_dependency),
        ) -> read_schema:
            try:
                existing_obj = await service.get_object_by_id(obj_id)
                if not existing_obj:
                    raise HTTPException(404, f"{forms['именительный'].capitalize()} не {forms['найден']}")

                data_dict = json.loads(form_data)
                
                data_dict.pop(file_field_name, None)

                if file and file.filename:
                    file_content = await file.read()
                    data_dict[file_field_name] = file_content
                else:
                    data_dict[file_field_name] = getattr(existing_obj, file_field_name)

                data_model = update_schema(**data_dict)
                result = await service.update_object(obj_id, data_model)

                return result
                
            except json.JSONDecodeError:
                raise HTTPException(400, detail="Невалидный JSON в form_data")
            except ValueError as e:
                raise HTTPException(400, detail=f"Ошибка обновления: {str(e)}")
    else:
        @router.post(
            "",
            response_model=read_schema,
            status_code=status.HTTP_201_CREATED,
            description=f"Создание нового {forms['родительный']}.",
        )
        async def create(
            data: create_schema, 
            service = Depends(service_dependency)
        ) -> read_schema:
            try:
                obj = await service.create_object(data)
                return obj
            except ValueError as e:
                logger.error(e)
                raise HTTPException(status_code=400, detail=f"Ошибка создания: {str(e)}")
    
    @router.get(
        "/{obj_id}",
        responses={404: {"description": f"{forms['именительный'].capitalize()} не {forms['найден']}"}},
        response_model=read_schema,
        description=f"Получение {forms['родительный']} по идентификатору.",
    )
    @cache(expire=settings.cache_ttl, coder=Base64Coder)
    async def get_by_id(
        obj_id: int,
        service: BaseService = Depends(service_dependency),
    ) -> read_schema:
        result = await service.get_object_by_id(obj_id)
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"{forms['именительный'].capitalize()} не {forms['найден']}"
            )
        return result
    
    if has_file_field:
        @router.put(
            "/{obj_id}", 
            response_model=read_schema, 
            description=f"Обновление {forms['родительный']} с файлом."
        )
        async def update(
            obj_id: int,
            file: Optional[UploadFile] = File(None),
            form_data: str = Form(...),
            service = Depends(service_dependency)
        ) -> read_schema:
            try:
                data_dict = json.loads(form_data)

                if file and file.filename:  
                    file_content = await file.read()
                    data_dict[file_field_name] = file_content
                elif file_field_name in data_dict:  
                    del data_dict[file_field_name]  

                data_model = update_schema(**data_dict)
                result = await service.update_object(obj_id, data_model)

                if not result:
                    raise HTTPException(404, f"{forms['именительный'].capitalize()} не {forms['найден']}")
                return result
            except json.JSONDecodeError:
                raise HTTPException(400, detail="Невалидный JSON в form_data")   
            except ValueError as e:
                raise HTTPException(400, detail=f"Ошибка обновления: {str(e)}")
    else:
        @router.put(
            "/{obj_id}", 
            response_model=read_schema, 
            description=f"Обновление {forms['родительный']}."
        )
        async def update(
            obj_id: int, 
            data: update_schema, 
            service = Depends(service_dependency)
        ) -> read_schema:
            try:
                result = await service.update_object(obj_id, data)
                if not result:
                    raise HTTPException(404, f"{forms['именительный'].capitalize()} не {forms['найден']}")
                return result
            except ValueError as e:
                raise HTTPException(400, detail=f"Ошибка обновления: {str(e)}")
    
    @router.delete(
        "/{obj_id}", 
        description=f"Удаление {forms['родительный']}.",
        responses={
            200: {"description": f"{forms['именительный'].capitalize()} успешно {forms['удален']}"},
            404: {"description": f"{forms['именительный'].capitalize()} не {forms['найден']}"}
        }
    )
    async def delete(
        obj_id: int, 
        service = Depends(service_dependency)
    ) -> Dict:
        success = await service.delete_object(obj_id)
        if not success:
            raise HTTPException(404, f"{forms['именительный'].capitalize()} не {forms['найден']}")
        return {"detail": f"{forms['именительный'].capitalize()} успешно {forms['удален']}"}
    
    if has_file_field:
        @router.get(
            "/{obj_id}/download",
            description=f"Скачивание файла {forms['родительный']}.",
            response_class=Response
        )
        @cache(settings.cache_ttl, coder=Base64Coder)
        async def download_file(
            obj_id: int,
            service = Depends(service_dependency)
        ):
            result = await service.get_object_by_id(obj_id)
            if not result:
                raise HTTPException(404, f"{forms['именительный'].capitalize()} не {forms['найден']}")
            
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
    
    return router