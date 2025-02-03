from typing import List, Type, Generic, TypeVar
from fastapi import APIRouter, Depends, HTTPException, status

from services.base import BaseService  # Обобщенный сервис
from schemas.base import BaseSchemaCreate, BaseSchemaUpdate, BaseSchemaInDB  # Базовые схемы
from depends import get_service  # Универсальный Depends для получения сервиса

# Обобщенные параметры
T = TypeVar("T")  # Модель
S = TypeVar("S", bound=BaseService)  # Сервис
CreateSchema = TypeVar("CreateSchema", bound=BaseSchemaCreate)  # Схема создания
UpdateSchema = TypeVar("UpdateSchema", bound=BaseSchemaUpdate)  # Схема обновления
InDBSchema = TypeVar("InDBSchema", bound=BaseSchemaInDB)  # Схема представления в БД


class BaseRouter(Generic[T, S, CreateSchema, UpdateSchema, InDBSchema]):
    def __init__(
        self,
        model: Type[T],
        service: Type[S],
        create_schema: Type[CreateSchema],
        update_schema: Type[UpdateSchema],
        in_db_schema: Type[InDBSchema],
        prefix: str,
        tags: list,
    ):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.service = service
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.in_db_schema = in_db_schema

        self._add_routes()

    def _add_routes(self):
        """Добавляет маршруты в API Router"""

        @self.router.get(
            "",
            responses={400: {"description": "Bad request"}},
            response_model=List[self.in_db_schema],
            description=f"Получение списка {self.model.__name__.lower()}",
        )
        async def get_all(service: self.service = Depends(get_service(self.service))):
            objects = await service.get_all_objects()
            return objects or []

        @self.router.post(
            "",
            status_code=status.HTTP_201_CREATED,
            response_model=self.create_schema,
            description=f"Создание {self.model.__name__.lower()}",
        )
        async def create(
            data: self.create_schema, service: self.service = Depends(get_service(self.service))
        ):
            try:
                obj = await service.create_object(data)
                return obj
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        @self.router.get(
            "/{obj_id}",
            responses={400: {"description": "Bad request"}},
            response_model=self.in_db_schema,
            description=f"Получение {self.model.__name__.lower()} по ID",
        )
        async def get_by_id(obj_id: int, service: self.service = Depends(get_service(self.service))):
            obj = await service.get_object_by_id(obj_id)
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} не найден."
                )
            return obj

        @self.router.put(
            "/{obj_id}",
            response_model=self.update_schema,
            description=f"Обновление {self.model.__name__.lower()}",
        )
        async def update(
            obj_id: int,
            data: self.update_schema,
            service: self.service = Depends(get_service(self.service)),
        ):
            obj = await service.update_object(obj_id, data)
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} не найден."
                )
            return obj

        @self.router.delete(
            "/{obj_id}",
            description=f"Удаление {self.model.__name__.lower()}",
        )
        async def delete(obj_id: int, service: self.service = Depends(get_service(self.service))):
            success = await service.delete_object(obj_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} не найден."
                )
            return {"detail": f"{self.model.__name__} успешно удалён."}
