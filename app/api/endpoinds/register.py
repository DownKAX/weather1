from fastapi import APIRouter, Depends, Form, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from passlib.hash import bcrypt
from datetime import datetime

from app.api.models.users import User, RegistrationForm
from app.core.security import create_jwt_token
from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService

auth = APIRouter(prefix='/register')

async def get_user_service(uow: AbstractUow = Depends(Uow)):
    return UserService(uow)

async def get_city_service(uow: AbstractUow = Depends(Uow)):
    return CitiesService(uow)



@auth.put('/signup')
async def register(credentials: RegistrationForm = Form(...),
                   user_service = Depends(get_user_service), city_service = Depends(get_city_service)):
    city_id = await city_service.select_city({'city_name': credentials.city}, return_value='id')
    if not city_id:
        raise HTTPException(status_code=404, detail='City not found')
    hashed_password = bcrypt.hash(credentials.password)
    user_data = User(username=credentials.username, password=hashed_password, register_time=datetime.now(), city_id=city_id, telegram_id=credentials.telegram_id)
    await user_service.add_user(user_data)
    return user_data

@auth.post('/login')
async def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends(), user_service = Depends(get_user_service)):
    user: User = await user_service.select_user({'username': credentials.username})
    if not bcrypt.verify(credentials.password, user.password):
        raise HTTPException(status_code=401, detail='Incorrect password')
    data: [dict | None] = {'username': user.username, 'password': user.password}
    token = await create_jwt_token(data)
    response.set_cookie(key='token', value=token)
    return user