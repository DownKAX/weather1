from celery import Celery
from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "app", ".env"))


scheduler = Celery('tg_messages', broker='redis://localhost:6379/0')

scheduler.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

scheduler.conf.beat_schedule = {
    'send_newsletter': {
        'task': 'celery_tasks.send_newsletter_task',
        'schedule': timedelta(seconds=7),
        'args': (3, ),
    }
}