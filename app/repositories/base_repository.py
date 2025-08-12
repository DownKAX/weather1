from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert, join
from typing import Any

from app.api.models.users import QueryFilter
from app.database.models import User, Cities


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data):
        ...

    @abstractmethod
    async def get_all_data(self):
        ...

    @abstractmethod
    async def get_one_by_column(self, columns_and_values: dict[str, Any]):
        ...

    @abstractmethod
    async def delete_by_id(self, id):
        ...

    @abstractmethod
    async def update_one(self, id: int, values):
        ...

class Repository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict):
        query = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_all_data(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_by_column(self, columns_and_values: dict[str, Any]):
        query = select(self.model).where(*(getattr(self.model, column) == value
                                           for column, value in columns_and_values.items()))
        result = await self.session.execute(query)
        result = result.fetchone()[0]
        return result

    async def get_all_by_column(self, columns_and_values: dict[str, Any]):
        query = select(self.model).where(*(getattr(self.model, column) == value
                                           for column, value in columns_and_values.items()))
        result = await self.session.execute(query)
        result = result.fetchmany()
        return result

    async def delete_by_id(self, id: int):
        query = delete(self.model).where(self.model.id == id).returning(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def update_one(self, column_name: str, column_value, values: dict):
        column = getattr(self.model, column_name)
        query = update(self.model).where(column == column_value).values(**values).returning(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_unique_values(self, column_name: str, filter: QueryFilter | None = None):
        column = getattr(self.model, column_name)
        query = select(column).distinct()
        if filter:
            filter_col = getattr(self.model, filter.column)
            query = query.where(filter_col == filter.value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def inner_join_with_filter(self, second_model, clause_1, clause_2, return_value: tuple, filter: QueryFilter | None = None):
        models = (self.model, second_model)
        clause_1 = getattr(self.model, clause_1)
        clause_2 = getattr(second_model, clause_2)
        column = getattr(models[return_value[0]], return_value[1])
        query = select(column).distinct().join(models[int(not return_value[0])], clause_1 == clause_2)

        if filter:
            filter_column = getattr(second_model, filter.column)
            query = query.where(filter_column == filter.value)
        result = await self.session.execute(query)
        return result.scalars().all()






class UserRepository(Repository):
    model = User

class CitiesRepository(Repository):
    model = Cities