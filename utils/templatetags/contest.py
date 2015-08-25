# coding=utf-8
import datetime
from django.utils.timezone import now


def get_contest_status(contest):
    status = contest.status
    if status == 1:
        return "没有开始"
    elif status == -1:
        return "已经结束"
    else:
        return "正在进行"


def get_contest_status_color(contest):
    status = contest.status
    if status == 1:
        return "info"
    elif status == -1:
        return "warning"
    else:
        return "success"


from django import template

register = template.Library()
register.filter("contest_status", get_contest_status)
register.filter("contest_status_color", get_contest_status_color)

