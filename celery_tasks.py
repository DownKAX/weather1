from httpx import AsyncClient
import celery
import asyncio
from aiogram import Bot

from celery_scheduler import scheduler
from app.database.models import Cities
from app.middleware.middleware import logger
from app.repositories.models import QueryFilter
from app.services.db_services import UserService
from app.telegram_bot.bot import send_newsletter_message
from app.utils.uow import Uow
from app.core.settings import settings

class LoggedTask(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Schedule task - {task_id} failed: {exc}")
        print('!!')

@scheduler.task(base=LoggedTask)
def send_newsletter_task(timezone):
    asyncio.run(send_newsletter(timezone))

async def send_newsletter(timezone):
    async with Bot(settings.TELEGRAM_API) as bot:
        city_ids = await UserService(Uow()).user_cities_by_timezone(Cities, 'city_id', 'id', (0, "city_id"),
                                                                    QueryFilter(column='timezone', value=timezone))
        for city_id in city_ids:
            users_in_city: list[int] = await UserService(Uow()).select_users({'city_id': city_id, 'newsletter': True},
                                                                             return_value='telegram_id')
            async with AsyncClient() as client:
                body = {'city_id': city_id, 'forecast_range': 'Прогноз на сегодня'}
                forecast = await client.post('http://127.0.0.1:80/user/get_forecast', data=body)
                forecast = forecast.json().get('forecast')
                if not forecast:
                    logger.error("Failed to get forecast")
            for user in users_in_city:
                try:
                    await send_newsletter_message(user, forecast, tg_bot=bot)
                except Exception as e:
                    logger.error(f"Error sending forecast: {e}\n")