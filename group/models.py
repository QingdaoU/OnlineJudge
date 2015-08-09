# coding=utf-8
from django.db import models

from account.models import User


class Group(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, related_name="my_groups")
    # 0是公开 1是需要申请后加入 2是不允许任何人加入
    join_group_setting = models.IntegerField()
    members = models.ManyToManyField(User)
    # 解散小组后，这一项改为False
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "group"


class JoinGroupRequest(models.Model):
    group = models.ForeignKey(User)
    user = models.ForeignKey(User, related_name="my_join_group_requests")
    message = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    # 是否处理
    status = models.BooleanField(default=False)

    class Meta:
        db_table = "join_group_request"
