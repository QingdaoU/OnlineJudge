# coding=utf-8
from django.db import models
from django.utils.timezone import now

from account.models import User
from problem.models import AbstractProblem
from group.models import Group

GROUP_CONTEST = 0
PUBLIC_CONTEST = 1
PASSWORD_PROTECTED_CONTEST = 2


class Contest(models.Model):
    title = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    # 比赛模式：0 即为是acm模式，1 即为是按照总的 ac 题目数量排名模式
    mode = models.IntegerField()
    # 是否显示实时排名结果
    real_time_rank = models.BooleanField()
    # 是否显示别人的提交记录
    show_user_submission = models.BooleanField()
    # 只能超级管理员创建公开赛，管理员只能创建小组内部的比赛
    # 如果这一项不为空，即为有密码的公开赛，没有密码的可以为小组赛或者是公开赛（此时用比赛的类型来表示）
    password = models.CharField(max_length=30, blank=True, null=True)
    # 比赛的类型： 0 即为是小组赛(GROUP_CONTEST)，1 即为是无密码的公开赛(PUBLIC_CONTEST)，
    # 2 即为是有密码的公开赛(PASSWORD_PUBLIC_CONTEST)
    contest_type = models.IntegerField()
    # 开始时间
    start_time = models.DateTimeField()
    # 结束时间
    end_time = models.DateTimeField()
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 最后修改时间
    last_updated_time = models.DateTimeField(auto_now=True)
    # 这个比赛是谁创建的
    created_by = models.ForeignKey(User)
    groups = models.ManyToManyField(Group)
    # 是否可见 false的话相当于删除
    visible = models.BooleanField(default=True)

    @property
    def status(self):
        if self.start_time > now():
            # 没有开始 返回1
            return 1
        elif self.end_time < now():
            # 已经结束 返回-1
            return -1
        else:
            # 正在进行 返回0
            return 0

    class Meta:
        db_table = "contest"


class ContestProblem(AbstractProblem):
    contest = models.ForeignKey(Contest)
    # 比如A B 或者1 2 或者 a b 将按照这个排序
    sort_index = models.CharField(max_length=30)
    score = models.IntegerField(default=0)

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


class ContestSubmission(models.Model):
    """
    用于保存比赛提交和排名的一些数据，加快检索速度
    """
    user = models.ForeignKey(User)
    problem = models.ForeignKey(ContestProblem)
    contest = models.ForeignKey(Contest)
    total_submission_number = models.IntegerField(default=1)
    # 这道题是 AC 还是没过
    ac = models.BooleanField()
    # ac 用时以秒计
    ac_time = models.IntegerField(default=0)
    # 总的时间，用于acm 类型的，也需要保存罚时
    total_time = models.IntegerField(default=0)
    # 第一个解出此题目
    first_achieved = models.BooleanField(default=False)

    class Meta:
        db_table = "contest_submission"
