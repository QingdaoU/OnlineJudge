# coding=utf-8
from django.db import models

from account.models import User


class Announcement(models.Model):
    # 标题
    title = models.CharField(max_length=50)
    # 公告的内容 HTML 格式
    content = models.TextField()
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 这个公告是谁创建的
    created_by = models.ForeignKey(User)
    # 是否可见 false的话相当于删除
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "announcement"
