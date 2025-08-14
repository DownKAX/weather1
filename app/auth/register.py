from fastapi import APIRouter, Form, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from datetime import datetime

from app.auth.exceptions import InvalidPasswordException, ExpiredAccessToken, InvalidRefreshToken
from app.auth.models import Tokens
from app.api.models.users import User, RegistrationForm
from app.auth.security import  get_tokens, check_session, verification_stamp, validate_token
from app.auth.dependencies import *
from app.auth.redis_repository import get_session


auth = APIRouter(prefix='/register')

@auth.put('/signup')
async def register(user_service: user_dependency, city_service: city_dependency,
                   credentials: RegistrationForm = Form(...)):
    city_id = await city_service.select_city({'city_name': credentials.city}, return_value='id')
    if not city_id:
        raise HTTPException(status_code=404, detail='City not found')
    hashed_password = bcrypt.hash(credentials.password)
    user_data = User(username=credentials.username, password=hashed_password, register_time=datetime.now(), city_id=city_id, telegram_id=credentials.telegram_id)
    await user_service.add_user(user_data)
    return user_data

@auth.post('/login')
async def login(useragent: useragent_dependency, user_service: user_dependency, response: Response,
                credentials: OAuth2PasswordRequestForm = Depends()):
    user: User = await user_service.select_user({'username': credentials.username})
    if not bcrypt.verify(credentials.password, user.password):
        raise InvalidPasswordException
    await verification_stamp(user.username, response, useragent)

@auth.post('/check_token')
async def check_token(request: Request, response: Response, useragent: useragent_dependency):
    tokens: Tokens = await get_tokens(request)
    try:
        payload = await validate_token(tokens.access_token)
    except ExpiredAccessToken:
        tokens: Tokens = await update_tokens(request, response, useragent)
        payload = await validate_token(tokens.access_token)
    return payload

@auth.post('/update_tokens')
async def update_tokens(request: Request, response: Response, useragent):
    tokens: Tokens = await get_tokens(request)
    session_in_redis = await get_session(tokens.refresh_token)
    if session_in_redis:
        await check_session(useragent, session_in_redis)
        tokens = await verification_stamp(session_in_redis.user, response, useragent)
        return tokens
    else:
        raise InvalidRefreshToken