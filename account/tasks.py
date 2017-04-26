from celery import shared_task

from utils.shortcuts import send_email


@shared_task
def send_email_async(from_name, to_email, to_name, subject, content):
    send_email(from_name, to_email, to_name, subject, content)
