# coding=utf-8
import datetime
from account.models import User


def get_username(user_id):
    try:
        return User.objects.get(id=user_id).username
    except User.DoesNotExist:
        return ""


from django import template

register = template.Library()
register.filter("get_username", get_username)

