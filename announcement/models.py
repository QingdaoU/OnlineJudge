# coding=utf-8
from django.db import models

from account.models import User
from group.models import Group
from utils.models import RichTextField


class Announcement(models.Model):
    title = models.CharField(max_length=50)
    # HTML
    content = RichTextField()
    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    last_update_time = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "announcement"
