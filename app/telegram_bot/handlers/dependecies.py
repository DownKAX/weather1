from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService
from typing import Annotated
from aiogram_dependency import Depends, Scope

async def get_user_service(uow: AbstractUow = Uow()):
    return UserService(uow)

async def get_city_service(uow: AbstractUow = Uow()):
    return CitiesService(uow)

user_dependency = Annotated[UserService, Depends(get_user_service, scope=Scope.TRANSIENT)]
cities_dependency = Annotated[CitiesService, Depends(get_city_service, scope=Scope.TRANSIENT)]