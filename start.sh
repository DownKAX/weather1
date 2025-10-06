#!/bin/sh
python app/main.py &
celery -A celery_tasks worker --pool=solo &
celery -A celery_tasks beat &
wait