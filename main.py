import asyncio
import pathlib

import uvicorn
import multiprocessing
from fastapi import FastAPI
from app.auth.register import auth
from app.api.endpoinds.user import user
from app.middleware.middleware import logging_middleware
from dotenv import load_dotenv
load_dotenv()
from app.core.settings import settings

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
    path = pathlib.Path('app', 'utils', 'forecast_plots').mkdir(parents=True, exist_ok=True)
    setup_tasks()
    multiprocessing.Process(target=bot_main).start()
    if not settings.DOCKER:
        multiprocessing.Process(target=main).start()

