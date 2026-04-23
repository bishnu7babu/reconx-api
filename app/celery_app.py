from celery import Celery
from pygments.lexer import include

from app.config import settings

celery_app = Celery(
    "reconx",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.nmap_task",
        "app.tasks.theharvester_task",
        "app.tasks.subfinder_task"
    ]
)