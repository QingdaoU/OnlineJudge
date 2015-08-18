# coding=utf-8
from django.db import models

from account.models import User
from group.models import Group


class Announcement(models.Model):
    # 标题
    title = models.CharField(max_length=50)
    # 公告的内容 HTML 格式
    content = models.TextField()
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 这个公告是谁创建的
    created_by = models.ForeignKey(User)
    # 最后更新时间
    last_update_time = models.DateTimeField(auto_now=True)
    # 是否可见 false的话相当于删除
    visible = models.BooleanField(default=True)
    # 公告可见范围 0是全局可见 1是部分小组可见，需要在下面的字段中存储可见的小组
    is_global = models.BooleanField()
    groups = models.ManyToManyField(Group)

    class Meta:
        db_table = "announcement"
