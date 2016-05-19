# coding=utf-8
from django.db import models


class JudgeServer(models.Model):
    name = models.CharField(max_length=30)
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    # 这个服务器最大可能运行的判题实例数量
    max_instance_number = models.IntegerField()
    used_instance_number = models.IntegerField(default=0)
    token = models.CharField(max_length=30)
    # status 为 false 的时候代表不使用这个服务器
    status = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = "judge_server"


class JudgeWaitingQueue(models.Model):
    submission_id = models.CharField(max_length=40)
    time_limit = models.IntegerField()
    memory_limit = models.IntegerField()
    test_case_id = models.CharField(max_length=40)
    create_time = models.DateTimeField(auto_now_add=True)
    spj = models.BooleanField(default=False)
    spj_language = models.IntegerField(blank=True, null=True)
    spj_code = models.TextField(blank=True, null=True)
    spj_version = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = "judge_waiting_queue"
