from django.db import models
from django.utils import timezone


class JudgeServer(models.Model):
    hostname = models.CharField(max_length=128)
    ip = models.CharField(max_length=32, blank=True, null=True)
    judger_version = models.CharField(max_length=32)
    cpu_core = models.IntegerField()
    memory_usage = models.FloatField()
    cpu_usage = models.FloatField()
    last_heartbeat = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    task_number = models.IntegerField(default=0)
    service_url = models.CharField(max_length=256, blank=True, null=True)
    is_disabled = models.BooleanField(default=False)

    @property
    def status(self):
        # 增加一秒延时，提高对网络环境的适应性
        if (timezone.now() - self.last_heartbeat).total_seconds() > 6:
            return "abnormal"
        return "normal"

    class Meta:
        db_table = "judge_server"
