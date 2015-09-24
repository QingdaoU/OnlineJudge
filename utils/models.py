# coding=utf-8
import json
from django.db import models

from utils.xss_filter import XssHtml


class RichTextField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        if not value:
            value = ""
        parser = XssHtml()
        parser.feed(value)
        parser.close()
        return parser.getHtml()


class JsonField(models.TextField):
    pass