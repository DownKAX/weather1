from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from typing import Annotated
from aiogram_dependency import Depends, Scope
from fastapi.exceptions import HTTPException

from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService

async def get_user_service(uow: AbstractUow = Uow()):
    return UserService(uow)

async def get_city_service(uow: AbstractUow = Uow()):
    return CitiesService(uow)

user_dependency = Annotated[UserService, Depends(get_user_service, scope=Scope.TRANSIENT)]
cities_dependency = Annotated[CitiesService, Depends(get_city_service, scope=Scope.TRANSIENT)]

class RegisteredFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        user_service = await get_user_service()
        try:
            db_user_id = await user_service.select_user({"telegram_id": obj.from_user.id})
        except HTTPException:
            return None
        return bool(db_user_id)