import asyncio
import multiprocessing
import uvicorn

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

def apscheduler_main():
    from app.scheduler import main as scheduler_main
    asyncio.run(scheduler_main())

if __name__ == '__main__':
    multiprocessing.Process(target=main).start()
    multiprocessing.Process(target=bot_main).start()
    multiprocessing.Process(target=apscheduler_main).start()

