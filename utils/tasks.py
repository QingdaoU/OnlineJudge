import os
import dramatiq

from utils.shortcuts import DRAMATIQ_WORKER_ARGS


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def delete_files(*args):
    for item in args:
        try:
            os.remove(item)
        except Exception:
            pass
