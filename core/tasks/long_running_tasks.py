import time
from config.celery_worker_config import celery_app


@celery_app.task
def long_running_task(duration: int):
    """
    A sample long-running task that can be passed to Celery.
    """
    print(f"Starting long running task for {duration} seconds...")
    time.sleep(duration)
    result = f"Task completed after {duration} seconds."
    print(result)
    return result