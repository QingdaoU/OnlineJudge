from django.db import models
from django.utils import timezone


class SMTPConfig(models.Model):
    server = models.CharField(max_length=128)
    port = models.IntegerField(default=25)
    email = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    tls = models.BooleanField()

    class Meta:
        db_table = "smtp_config"


class WebsiteConfig(models.Model):
    base_url = models.CharField(max_length=128, default="http://127.0.0.1")
    name = models.CharField(max_length=32, default="Online Judge")
    name_shortcut = models.CharField(max_length=32, default="oj")
    footer = models.TextField(default="Online Judge Footer")
    # allow register
    allow_register = models.BooleanField(default=True)
    # submission list show all user's submission
    submission_list_show_all = models.BooleanField(default=True)

    class Meta:
        db_table = "website_config"


class JudgeServer(models.Model):
    hostname = models.CharField(max_length=64)
    ip = models.CharField(max_length=32, blank=True, null=True)
    judger_version = models.CharField(max_length=24)
    cpu_core = models.IntegerField()
    memory_usage = models.FloatField()
    cpu_usage = models.FloatField()
    last_heartbeat = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    task_number = models.IntegerField(default=0)
    service_url = models.CharField(max_length=128, blank=True, null=True)

    @property
    def status(self):
        # 增加一秒延时，提高对网络环境的适应性
        if (timezone.now() - self.last_heartbeat).total_seconds() > 6:
            return "abnormal"
        return "normal"

    class Meta:
        db_table = "judge_server"


class JudgeServerToken(models.Model):
    token = models.CharField(max_length=32)

    class Meta:
        db_table = "judge_server_token"
