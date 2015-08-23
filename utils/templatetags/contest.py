# coding=utf-8
import datetime
from django.utils.timezone import now


def get_contest_status(contest):
    if contest.start_time > now():
        return "没有开始"
    if contest.end_time < now():
        return "已经结束"
    return "正在进行"


def get_contest_status_color(contest):
    if contest.start_time > now():
        return "info"
    if contest.end_time < now():
        return "warning"
    return "success"


from django import template

register = template.Library()
register.filter("contest_status", get_contest_status)
register.filter("contest_status_color", get_contest_status_color)

