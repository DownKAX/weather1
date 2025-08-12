from typing import Any

from app.utils.uow import Uow
from app.repositories.base_repository import UserRepository, CitiesRepository
from app.api.models.users import User, City, QueryFilter
from app.database.models import Cities
from fastapi import HTTPException
from datetime import datetime

from app.utils.common_validators import unique_check, exists_check

class UserService:
    UserOrScalar = User | str | int | datetime | bool
    Scalar = str | int | datetime | bool

    def __init__(self, uow: Uow):
        self.uow = uow

    async def select_user(self, columns_and_values: dict[str, Any], return_value: str | None = None) -> UserOrScalar:
        async with self.uow:
            result = await exists_check(self.uow.user_model.get_one_by_column, e_code=401, e_message='User does not exist',
                                        columns_and_values=columns_and_values)
            result: User = User.model_validate(result.__dict__)
            return result if not return_value else getattr(result, return_value)

    async def select_users(self, columns_and_values: dict[str, Any], return_value: str | None = None) -> list[User] | list[Scalar]:
        async with self.uow:
            result = await exists_check(self.uow.user_model.get_all_by_column, e_code=401, e_message='User does not exist',
                                        columns_and_values=columns_and_values)
            result: list[User] = [User.model_validate(us[0].__dict__) for us in result]
            return result if not return_value else [getattr(x, return_value) for x in result]

    async def add_user(self, data: User) -> User:
        data = data.model_dump()
        async with self.uow:
            result = await unique_check(self.uow.user_model.add_one, with_ermsg=True, e_code=401, e_message=' is already taken!', data=data)
            result: User = User.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    async def update_data(self, col_name: str, col_value, data: dict) -> User:
        async with self.uow:
            result = await unique_check(self.uow.user_model.update_one, e_code=401, e_message='Telegram id is busy',
                                        column_name=col_name, column_value=col_value, values=data)
            result: User = User.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    async def get_unique_values(self, col_name: str, filter: QueryFilter):
        async with self.uow:
            result = await self.uow.user_model.get_unique_values(col_name, filter)
            return result

    async def user_cities_by_timezone(self, clause_1, clause_2, return_value: str, filter: QueryFilter | None = None):
        async with self.uow:
            result = await self.uow.user_model.inner_join_with_filter(Cities, clause_1, clause_2, return_value, filter)
            return result




class CitiesService:
    CityOrScalar = City | str | int | float

    def __init__(self, uow: Uow):
        self.uow = uow

    async def select_city(self, columns_and_values: dict[str, Any], return_value: str | None = None) -> CityOrScalar | None:
        async with self.uow:
            try:
                result = await exists_check(self.uow.city_model.get_one_by_column, e_code=401, e_message='City not found',
                                        columns_and_values=columns_and_values)
            except HTTPException:
                return
            result: City = City.model_validate(result.__dict__)
            return result if not return_value else getattr(result, return_value)

    async def add_city(self, data: City):
        data: dict = data.model_dump()
        async with self.uow:
            try:
                result = await unique_check(self.uow.city_model.add_one, e_code=401,
                                            e_message='Such city already exists',data=data)
            except HTTPException:
                return
            result: City = City.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    async def get_unique_values(self, col_name: str, filter: None | QueryFilter = None):
        async with self.uow:
            result = await self.uow.city_model.get_unique_values(col_name, filter)
            return result