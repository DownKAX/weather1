import jwt
from datetime import datetime, timedelta, UTC
from fastapi import  Response, Request
from secrets import token_hex

from app.core.settings import settings
from app.auth.models import Tokens, Session, SessionForRedis
from app.auth.exceptions import TokenNotFoundException, ExpiredAccessToken, InvalidTokenError, ExpiredRefreshToken, \
    InvalidRefreshToken
from app.auth.redis_repository import add_session


async def create_access_token(user: str):
    data = {'username': user, 'exp': datetime.now(UTC) + timedelta(hours=4)}
    token = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
    return token

async def create_session(username: str, useragent: str) -> SessionForRedis:
    refresh_token = token_hex(8)
    session = Session(user=username, useragent=useragent)
    return SessionForRedis(refresh_token=refresh_token, session=session)

async def set_jwt_tokens(tokens: Tokens, response: Response):
    response.set_cookie(key="token", value=tokens.access_token)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token)
    return response

async def get_tokens(request: Request) -> Tokens:
    access_token = request.cookies.get("token")
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        return Tokens(access_token=access_token, refresh_token=refresh_token)
    else:
        raise TokenNotFoundException

async def get_useragent(request: Request):
    return request.headers.get("User-Agent")

async def validate_token(token):
    if token is None:
        raise TokenNotFoundException
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredAccessToken
    except jwt.InvalidTokenError:
        raise InvalidTokenError

async def check_session(useragent: str, session_in_redis):
    if session_in_redis.useragent != useragent:
        raise InvalidRefreshToken
    if session_in_redis.exp.timestamp() < datetime.now(UTC).timestamp():
        raise ExpiredRefreshToken
    return True

async def verification_stamp(username: str, response: Response, useragent: str):
    access_token = await create_access_token(user=username)
    session_with_refresh: SessionForRedis = await create_session(username, useragent)
    await set_jwt_tokens(Tokens(access_token=access_token, refresh_token=session_with_refresh.refresh_token), response)
    await add_session(username, refresh_token=session_with_refresh.refresh_token,
                      session=session_with_refresh.session)
    return Tokens(access_token=access_token, refresh_token=session_with_refresh.refresh_token)