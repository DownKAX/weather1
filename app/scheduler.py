from httpx import AsyncClient
from datetime import timedelta

from app.database.models import Cities
from app.repositories.models import QueryFilter
from app.services.db_services import CitiesService, UserService
from app.utils.uow import Uow
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.middleware.middleware import logger
from app.telegram_bot.bot import send_newsletter_message
import asyncio


async def send_newsletter(timezone):
    city_ids = await UserService(Uow()).user_cities_by_timezone(Cities, 'city_id', 'id', (0, "city_id"), QueryFilter(column='timezone', value=timezone))
    for city_id in city_ids:
        users_in_city: list[int] = await UserService(Uow()).select_users({'city_id': city_id, 'newsletter': True}, return_value='telegram_id')
        async with AsyncClient() as client:
            body = {'city_id': city_id, 'forecast_range': 'Прогноз на сегодня'}
            forecast = await client.post('http://localhost:80/user/get_forecast', data=body)
            forecast = forecast.json().get('forecast')
        for user in users_in_city:
            try:
                await send_newsletter_message(user, forecast)
            except Exception as e:
                logger.error(f"Error sending forecast: {e}\n")


def schedule_daily_messages(scheduler, timezone):
    hour = timedelta(hours=7) - timedelta(hours=timezone)
    hour = int(hour.seconds / 60 / 60)
    scheduler.add_job(
        func=send_newsletter,
        trigger='cron',
        hour=hour,
        id=f'newsletter_{hour}',
        name='Рассылка прогноза погоды на сегодня',
        args=[timezone],
        replace_existing=True
    )

async def main():
    scheduler = AsyncIOScheduler(timezone="UTC")
    timezones = await CitiesService(Uow()).get_unique('timezone')
    for timezone in timezones:
        schedule_daily_messages(scheduler, timezone)
    scheduler.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
