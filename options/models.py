from django.db import models
from jsonfield import JSONField


class SysOptions(models.Model):
    key = models.CharField(max_length=128, unique=True, db_index=True)
    value = JSONField()
