from django.db import models
from utils.models import JSONField


class SysOptions(models.Model):
    key = models.TextField(unique=True, db_index=True)
    value = JSONField()
