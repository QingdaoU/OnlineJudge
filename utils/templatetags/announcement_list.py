# coding=utf-8
from django import template

from announcement.models import Announcement


def public_announcement_list():
    return Announcement.objects.filter(visible=True).order_by("-create_time")

register = template.Library()
register.assignment_tag(public_announcement_list, name="public_announcement_list")