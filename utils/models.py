# coding=utf-8
import json
from django.db import models

from utils.xss_filter import XssHtml
import sys

class RichTextField(models.TextField):
    if sys.version_info < (3,):
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