# coding=utf-8
from django.db import models

from account.models import User
from problem.models import AbstractProblem


class Contest(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField()
    # 比赛模式 现在有 acm 模式，按照 ac 题目数量得分模式，
    # 按照 ac 的题目的总分得分模式和按照通过的测试用例总分得分模式等
    mode = models.IntegerField()
    # 是否显示排名结果
    show_rank = models.BooleanField()
    # 如果这一项不为空，那这就不是公开赛，需要密码才能进入
    password = models.CharField(max_length=30, blank=True, null=True)
    # 开始时间
    start_time = models.DateTimeField()
    # 结束时间
    end_time = models.DateTimeField()
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 最后修改时间
    last_updated_time = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)

    class Meta:
        db_table = "contest"


class ContestProblem(AbstractProblem):
    contest = models.ForeignKey(Contest)
    # 比如A B 或者1 2 或者 a b 将按照这个排序
    sort_index = models.CharField(max_length=30)

    class Meta:
        db_table = "contest_problem"


class ContestProblemTestCase(models.Model):
    """
    如果比赛是按照通过的测试用例总分计算的话，就需要这个model 记录每个测试用例的分数
    """
    # 测试用例的id 这个还在测试用例的配置文件里面有对应
    id = models.CharField(max_length=40, primary_key=True, db_index=True)
    problem = models.ForeignKey(ContestProblem)
    score = models.IntegerField()

    class Meta:
        db_table = "contest_problem_test_case"
