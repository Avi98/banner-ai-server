import threading
from celery import Celery
from config.env_variables import get_settings


_celery_app = None
_celery_lock = threading.Lock()


def get_celery_instance():
    global _celery_app
    settings = get_settings()

    if _celery_app is None:
        with _celery_lock:

            _celery_app = Celery(
                "ai-worker-thread",
                broker=settings.CELERY_BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND
            )

    return _celery_app


celery_app: Celery = get_celery_instance()
celery_app.autodiscover_tasks(['core.tasks'])
