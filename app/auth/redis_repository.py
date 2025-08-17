import json
from app.auth.models import Session
from app.my_redis_client import get_redis


async def add_session(user: str, refresh_token: str, session: Session):
    r = await get_redis()
    r.hset(user, refresh_token, session.model_dump_json())
    r.hset('refresh_tokens', refresh_token, user)

async def get_session(refresh_token: str) -> Session:
    r = await get_redis()
    username = r.hget('refresh_tokens', refresh_token)
    if username:
        session_in_redis = r.hget(username, refresh_token)
        if session_in_redis:
            session_in_redis = Session(**json.loads(session_in_redis))
        return session_in_redis