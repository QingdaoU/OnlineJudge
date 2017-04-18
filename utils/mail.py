#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from envelopes import Envelope

from conf.models import SMTPConfig


def send_email(from_name, to_email, to_name, subject, content):
    smtp = SMTPConfig.objects.first()
    if not smtp:
        return
    envlope = Envelope(from_addr=(smtp.email, from_name),
                       to_addr=(to_email, to_name),
                       subject=subject,
                       html_body=content)
    envlope.send(smtp.server,
                 login=smtp.email,
                 password=smtp.password,
                 port=smtp.port,
                 tls=smtp.tls)
