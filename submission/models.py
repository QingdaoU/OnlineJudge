from django.db import models
from jsonfield import JSONField

from utils.models import RichTextField
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
    created_time = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(db_index=True)
    code = RichTextField()
    result = models.IntegerField(default=JudgeStatus.PENDING)
    # 判题结果的详细信息
    info = JSONField(default={})
    language = models.CharField(max_length=20)
    shared = models.BooleanField(default=False)
    # 题目状态为 Accepted 时才会存储相关info
    accepted_time = models.IntegerField(blank=True, null=True)
    accepted_info = JSONField(default={})

    class Meta:
        db_table = "submission"

    def __str__(self):
        return self.id
