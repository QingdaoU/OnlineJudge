# coding=utf-8
from django.db import models

from account.models import User


class Group(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="my_groups")
    # 0是公开 1是需要申请后加入 2是不允许任何人加入
    join_group_setting = models.IntegerField(default=1)
    members = models.ManyToManyField(User, through="UserGroupRelation")
    admin = models.ManyToManyField(User, through="AdminGroupRelation", related_name="managed_groups")
    # 解散小组后，这一项改为False
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "group"


class UserGroupRelation(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    join_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "user_group_relation"
        unique_together = ("group", "user")
        


class AdminGroupRelation(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    
    class Meta:
        db_table = "admin_group_relation"
        unique_together = ("user", "group")


class JoinGroupRequest(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User, related_name="my_join_group_requests")
    message = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    # 是否处理
    status = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = "join_group_request"
