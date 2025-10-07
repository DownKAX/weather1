import asyncio
import uvicorn
import multiprocessing
from fastapi import FastAPI

from app.auth.register import auth
from app.api.endpoinds.user import user
from app.middleware.middleware import logging_middleware

app = FastAPI()
app.include_router(auth)
app.include_router(user)
app.middleware('http')(logging_middleware)

def main():
    uvicorn.run(app, host='0.0.0.0', port=80)

def bot_main():
    from app.telegram_bot.bot import main
    asyncio.run(main())

def setup_tasks():
    from app.services.db_services import CitiesService
    from app.utils.uow import Uow
    import asyncio
    from my_redis_client import get_sync_redis

    timezones = asyncio.run(CitiesService(Uow()).get_unique('timezone'))
    r = get_sync_redis()
    for tz in timezones:
        r.sadd('timezones', tz)

if __name__ == '__main__':
    setup_tasks()
    multiprocessing.Process(target=main).start()
    multiprocessing.Process(target=bot_main).start()

