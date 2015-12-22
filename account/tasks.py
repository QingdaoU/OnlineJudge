# coding=utf-8
from celery import shared_task
from utils.mail import send_email


@shared_task
def _send_email(from_name, to_email, to_name, subject, content):
    send_email(from_name, to_email, to_name, subject, content)