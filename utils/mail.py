# coding=utf-8
from envelopes import Envelope

from django.conf import settings


def send_email(from_name, to_email, to_name, subject, content):
    envelope = Envelope(from_addr=(settings.SMTP_CONFIG["email"], from_name),
                        to_addr=(to_email, to_name),
                        subject=subject,
                        html_body=content)
    envelope.send(settings.SMTP_CONFIG["smtp_server"],
                  login=settings.SMTP_CONFIG["email"],
                  password=settings.SMTP_CONFIG["password"],
                  tls=settings.SMTP_CONFIG["tls"])
