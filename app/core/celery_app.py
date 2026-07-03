
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "pulseai",
    broker="redis://localhost:6379/0",    
    backend="redis://localhost:6379/1",   
    include=[
        "app.tasks.notification_tasks",   
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,

    beat_schedule={
        "hourly-event-summary": {
            "task": "app.tasks.notification_tasks.hourly_event_summary",
            "schedule": crontab(minute=0, hour="*"),  # every hour at :00
        },
    },
)