from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService
from typing import Annotated

async def get_user_service(uow: AbstractUow = Uow()):
    return UserService(uow)

user_dependency = Annotated[UserService, get_user_service()]
cities_dependency = Annotated[CitiesService, get_user_service()]