from django.db.models import JSONField  # NOQA
from django.db import models

from utils.xss_filter import XSSHtml


class RichTextField(models.TextField):
    def get_prep_value(self, value):
        with XSSHtml() as parser:
            return parser.clean(value or "")
