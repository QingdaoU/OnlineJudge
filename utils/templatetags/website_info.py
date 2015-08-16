# coding=utf-8
from django import template
register = template.Library()


@register.simple_tag
def show_website_info(name):
    return {"website_name": "qduoj", "website_footer": u"青岛大学信息工程学院 创新实验室"}[name]
