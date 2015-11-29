# coding=utf-8
from django.db import models


class JudgeServer(models.Model):
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    # 这个服务器最大可能运行的判题实例数量
    max_instance_number = models.IntegerField()
    left_instance_number = models.IntegerField()
    # status 为 false 的时候代表不使用这个服务器
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "judge_server"
