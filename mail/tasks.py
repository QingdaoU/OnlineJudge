# coding=utf-8
import os
from envelopes import Envelope

SMTP_CONFIG = {"smtp_server": "smtp.mxhichina.com",
               "email": "noreply@qduoj.com",
               "password": os.environ.get("smtp_password", "111111"),
               "tls": False}


def send_email(from_name, to_email, to_name, subject, content):
    envelope = Envelope(from_addr=(SMTP_CONFIG["email"], from_name),
                        to_addr=(to_email, to_name),
                        subject=subject,
                        html_body=content)
    envelope.send(SMTP_CONFIG["smtp_server"],
                  login=SMTP_CONFIG["email"],
                  password=SMTP_CONFIG["password"],
                  tls=SMTP_CONFIG["tls"])
