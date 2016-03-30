# coding=utf-8
from django.db import models


class JudgeServer(models.Model):
    name = models.CharField(max_length=30)
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
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def use_judge_instance(self):
        # 因为use 和 release 中间是判题时间，可能这个 model 的数据已经被修改了，所以不能直接使用self.xxx，否则取到的是旧数据
        server = JudgeServer.objects.select_for_update().get(id=self.id)
        server.left_instance_number -= 1
        server.workload = 100 - int(float(server.left_instance_number) / server.max_instance_number * 100)
        server.save()

    def release_judge_instance(self):
        # 使用原子操作
        server = JudgeServer.objects.select_for_update().get(id=self.id)
        server.left_instance_number += 1
        server.workload = 100 - int(float(server.left_instance_number) / server.max_instance_number * 100)
        server.save()

    class Meta:
        db_table = "judge_server"


class JudgeWaitingQueue(models.Model):
    submission_id = models.CharField(max_length=40)
    time_limit = models.IntegerField()
    memory_limit = models.IntegerField()
    test_case_id = models.CharField(max_length=40)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "judge_waiting_queue"
