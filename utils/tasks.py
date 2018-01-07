import os
from celery import shared_task


@shared_task
def delete_files(*args):
    for item in args:
        try:
            os.remove(item)
        except Exception:
            pass
