# coding=utf-8
from django.db import models

from utils.xss_filter import XssHtml


class RichTextField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        if not value:
            return value
        parser = XssHtml()
        parser.feed(value)
        parser.close()
        return parser.getHtml()