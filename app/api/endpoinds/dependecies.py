from typing import Annotated
from fastapi import Depends

from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService

async def get_user_service(uow: AbstractUow = Depends(Uow)):
    return UserService(uow)

async def get_city_service(uow: AbstractUow = Depends(Uow)):
    return CitiesService(uow)

city_dependency = Annotated[CitiesService, Depends(get_city_service)]
user_dependency = Annotated[UserService, Depends(get_user_service)]
