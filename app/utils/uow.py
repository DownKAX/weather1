from abc import ABC, abstractmethod

from app.database.db import AsyncSessionMaker
from app.repositories.base_repository import UserRepository, CitiesRepository

class AbstractUow(ABC):
    model: None

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class Uow(AbstractUow):
    def __init__(self):
        self.session_maker = AsyncSessionMaker

    async def __aenter__(self):
        self.session = self.session_maker()
        self.user_model = UserRepository(self.session)
        self.city_model = CitiesRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
