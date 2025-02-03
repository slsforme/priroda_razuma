from abc import ABC, abstractmethod
from typing import List


class AbstractRepository(ABC):
    @abstractmethod
    async def add():
        raise NotImplementedError

    @abstractmethod
    async def get() -> List[...]:
        raise NotImplementedError

    @abstractmethod
    async def update():
        raise NotImplementedError

    @abstractmethod
    async def delete():
        raise NotImplementedError

    @abstractmethod
    async def get_by_id() -> ...:
        raise NotImplementedError
