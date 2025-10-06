from celery.schedules import crontab
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "app", ".env"))

from celery import Celery
from app.my_redis_client import get_sync_redis

host = os.getenv('REDIS_HOST')
broker_host = f'redis://{host}:6379/0'
scheduler = Celery('tg_messages', broker=broker_host)


scheduler.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

r = get_sync_redis()
timezones = r.smembers('timezones')
for tz in timezones:
    tz = int(tz)
    hour = 7 - tz
    if hour < 0:
        hour = 24 + hour
    scheduler.conf.beat_schedule[f'send_newsletter{tz}'] = \
        {
            'task': 'celery_tasks.send_newsletter_task',
            'schedule': crontab(hour=hour),
            'args': (tz,),
        }
