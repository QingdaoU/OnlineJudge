# coding=utf-8
from django.db import models


class JudgeServer(models.Model):
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    # 这个服务器最大可能运行的判题实例数量
    max_instance_number = models.IntegerField()
    left_instance_number = models.IntegerField()
    workload = models.IntegerField(default=0)
    token = models.CharField(max_length=30)
    # 进行测试用例同步的时候加锁
    lock = models.BooleanField(default=False)
    # status 为 false 的时候代表不使用这个服务器
    status = models.BooleanField(default=True)

    def use_judge_instance(self):
        self.left_instance_number -= 1
        self.workload = 100 - int(self.left_instance_number / self.max_instance_number)
        self.save()

    class Meta:
        db_table = "judge_server"


class JudgeWaitingQueue(models.Model):
    submission_id = models.CharField(max_length=40)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "judge_waiting_queue"
