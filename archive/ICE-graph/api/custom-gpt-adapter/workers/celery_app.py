from celery import Celery
from app.core.config import settings
from kombu import Queue

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.memory_processor"]
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    worker_concurrency=1,
    task_queues=(
        Queue("default"),
        Queue("memory_creation"),
    ),
    task_default_queue="default",
)

if __name__ == '__main__':
    celery_app.start() 