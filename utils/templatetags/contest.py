# coding=utf-8
import datetime
from django.utils.timezone import localtime


def get_contest_status(contest):
    now = datetime.datetime.now()
    if localtime(contest.start_time).replace(tzinfo=None) > now:
        return "没有开始"
    if localtime(contest.end_time).replace(tzinfo=None) < now:
        return "已经结束"
    return "正在进行"


def get_contest_status_color(contest):
    now = datetime.datetime.now()
    if localtime(contest.start_time).replace(tzinfo=None) > now:
        return "info"
    if localtime(contest.end_time).replace(tzinfo=None) < now:
        return "warning"
    return "success"


from django import template

register = template.Library()
register.filter("contest_status", get_contest_status)
register.filter("contest_status_color", get_contest_status_color)

