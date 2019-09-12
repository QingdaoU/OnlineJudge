import logging
import dramatiq

from options.options import SysOptions
from utils.shortcuts import send_email, DRAMATIQ_WORKER_ARGS

logger = logging.getLogger(__name__)


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS(max_retries=3))
def send_email_async(from_name, to_email, to_name, subject, content):
    if not SysOptions.smtp_config:
        return
    try:
        send_email(smtp_config=SysOptions.smtp_config,
                   from_name=from_name,
                   to_email=to_email,
                   to_name=to_name,
                   subject=subject,
                   content=content)
    except Exception as e:
        logger.exception(e)
