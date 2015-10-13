# coding=utf-8
from django import template
from django.conf import settings
register = template.Library()


@register.simple_tag
def show_website_info(name):
    return settings.WEBSITE_INFO[name]
