import logging

from celery import shared_task
from envelopes import Envelope

from options.options import SysOptions

logger = logging.getLogger(__name__)


def send_email(from_name, to_email, to_name, subject, content):
    smtp = SysOptions.smtp_config
    if not smtp:
        return
    envlope = Envelope(from_addr=(smtp["email"], from_name),
                       to_addr=(to_email, to_name),
                       subject=subject,
                       html_body=content)
    try:
        envlope.send(smtp["server"],
                     login=smtp["email"],
                     password=smtp["password"],
                     port=smtp["port"],
                     tls=smtp["tls"])
        return True
    except Exception as e:
        logger.exception(e)
        return False


@shared_task
def send_email_async(from_name, to_email, to_name, subject, content):
    send_email(from_name, to_email, to_name, subject, content)
