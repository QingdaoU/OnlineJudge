import logging

from celery import shared_task

from options.options import SysOptions
from utils.shortcuts import send_email

logger = logging.getLogger(__name__)


@shared_task
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
