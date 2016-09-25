# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from group.models import Group
from jsonfield import JSONField

from account.models import User
from problem.models import AbstractProblem
from utils.models import RichTextField


class ContestType(object):
    GROUP_CONTEST = 0
    PUBLIC_CONTEST = 1
    PASSWORD_PROTECTED_CONTEST = 2
    PASSWORD_PROTECTED_GROUP_CONTEST = 3


class ContestStatus(object):
    CONTEST_NOT_START = 1
    CONTEST_ENDED = -1
    CONTEST_UNDERWAY = 0


class ContestRuleType(object):
    ACM = 0
    OI = 1


class Contest(models.Model):
    title = models.CharField(max_length=40, unique=True)
    description = RichTextField()
    # show real time rank or cached rank
    real_time_rank = models.BooleanField()
    password = models.CharField(max_length=30, blank=True, null=True)
    # enum of ContestType
    contest_type = models.IntegerField()
    # enum of ContestRuleType
    rule_type = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)
    groups = models.ManyToManyField(Group)
    # 是否可见 false的话相当于删除
    visible = models.BooleanField(default=True)

    @property
    def status(self):
        if self.start_time > now():
            # 没有开始 返回1
            return ContestStatus.CONTEST_NOT_START
        elif self.end_time < now():
            # 已经结束 返回-1
            return ContestStatus.CONTEST_ENDED
        else:
            # 正在进行 返回0
            return ContestStatus.CONTEST_UNDERWAY

    class Meta:
        db_table = "contest"


class ContestProblem(AbstractProblem):
    contest = models.ForeignKey(Contest)
    # 比如A B 或者1 2 或者 a b 将按照这个排序
    sort_index = models.CharField(max_length=30)
    # 是否已经公开了题目，防止重复公开
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = "contest_problem"


class ContestRank(models.Model):
    user = models.ForeignKey(User)
    contest = models.ForeignKey(Contest)
    total_submission_number = models.IntegerField(default=0)

    class Meta:
        abstract = True


class ACMContestRank(ContestRank):
    total_ac_number = models.IntegerField(default=0)
    # total_time is only for ACM contest total_time =  ac time + none-ac times * 20 * 60
    total_time = models.IntegerField(default=0)
    # {23: {"is_ac": True, "ac_time": 8999, "error_number": 2, "is_first_ac": True}}
    # key is problem id
    submission_info = JSONField(default={})

    class Meta:
        db_table = "acm_contest_rank"


class OIContestRank(ContestRank):
    total_score = models.IntegerField(default=0)
    # {23: {"score": 80, "total_score": 100}}
    # key is problem id
    submission_info = JSONField(default={})

    class Meta:
        db_table = "oi_contenst_rank"