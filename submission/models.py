# coding=utf-8
from django.db import models
from utils.shortcuts import rand_str
from judge.result import result


class Submission(models.Model):
    id = models.CharField(max_length=32, default=rand_str, primary_key=True, db_index=True)
    user_id = models.IntegerField(db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)
    # 判题开始时间
    judge_start_time = models.BigIntegerField(blank=True, null=True)
    # 判题结束时间
    judge_end_time = models.BigIntegerField(blank=True, null=True)
    result = models.IntegerField(default=result["waiting"])
    language = models.IntegerField()
    code = models.TextField()
    contest_id = models.IntegerField(blank=True, null=True)
    problem_id = models.IntegerField(db_index=True)
    # 这个字段可能存储很多数据 比如编译错误、系统错误的时候，存储错误原因字符串
    # 正常运行的时候存储判题结果，比如cpu时间内存之类的
    info = models.TextField(blank=True, null=True)
    accepted_answer_time = models.IntegerField(blank=True, null=True)
    # 这个字段只有在题目是accepted 的时候才会用到，比赛题目的提交可能还会有得分等信息，存储在这里面
    accepted_answer_info = models.TextField(blank=True, null=True)
    # 是否可以分享
    shared = models.BooleanField(default=False)

    class Meta:
        db_table = "submission"

    def __unicode__(self):
        return self.id
