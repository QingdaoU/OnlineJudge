from django.contrib.postgres.fields import JSONField  # NOQA
from django.db import models

from utils.xss_filter import XssHtml


class RichTextField(models.TextField):
    def get_prep_value(self, value):
        if not value:
            value = ""
        parser = XssHtml()
        parser.feed(value)
        parser.close()
        return parser.getHtml()
