from typing import Annotated

from app.auth.security import get_useragent
from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService
from fastapi import Depends

async def get_user_service(uow: AbstractUow = Depends(Uow)):
    return UserService(uow)

async def get_city_service(uow: AbstractUow = Depends(Uow)):
    return CitiesService(uow)

useragent_dependency = Annotated[str, Depends(get_useragent)]
city_dependency = Annotated[CitiesService, Depends(get_city_service)]
user_dependency = Annotated[UserService, Depends(get_user_service)]
