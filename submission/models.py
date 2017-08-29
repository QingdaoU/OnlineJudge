from django.db import models
from jsonfield import JSONField
from account.models import AdminType

from utils.shortcuts import rand_str


class JudgeStatus:
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    CPU_TIME_LIMIT_EXCEEDED = 1
    REAL_TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5
    PENDING = 6
    JUDGING = 7
    PARTIALLY_ACCEPTED = 8


class Submission(models.Model):
    id = models.CharField(max_length=32, default=rand_str, primary_key=True, db_index=True)
    contest_id = models.IntegerField(db_index=True, null=True)
    problem_id = models.IntegerField(db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(db_index=True)
    username = models.CharField(max_length=30)
    code = models.TextField()
    result = models.IntegerField(default=JudgeStatus.PENDING)
    # 判题结果的详细信息
    info = JSONField(default={})
    language = models.CharField(max_length=20)
    shared = models.BooleanField(default=False)
    # 存储该提交所用时间和内存值，方便提交列表显示
    # {time_cost: "", memory_cost: "", err_info: "", score: 0}
    statistic_info = JSONField(default={})

    def check_user_permission(self, user):
        return self.user_id == user.id or \
               self.shared is True or \
               user.admin_type == AdminType.SUPER_ADMIN

    class Meta:
        db_table = "submission"
        ordering = ("-create_time",)

    def __str__(self):
        return self.id
