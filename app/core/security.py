import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.core.settings import settings

async def create_jwt_token(data: dict) -> str:
    data.update({"exp": datetime.now() + timedelta(days=2)})
    token = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
    return token

async def user_data_from_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail="Invalid token")