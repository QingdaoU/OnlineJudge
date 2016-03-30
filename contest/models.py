# coding=utf-8
import logging

from django.db import models
from django.utils.timezone import now

from account.models import User
from problem.models import AbstractProblem
from group.models import Group
from utils.models import RichTextField
from jsonfield import JSONField
from judge.result import result


GROUP_CONTEST = 0
PUBLIC_CONTEST = 1
PASSWORD_PROTECTED_CONTEST = 2
PASSWORD_PROTECTED_GROUP_CONTEST = 3

CONTEST_NOT_START = 1
CONTEST_ENDED = -1
CONTEST_UNDERWAY = 0


logger = logging.getLogger("app_info")


class Contest(models.Model):
    title = models.CharField(max_length=40, unique=True)
    description = RichTextField()
    # 是否显示实时排名结果
    real_time_rank = models.BooleanField()
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
            return CONTEST_NOT_START
        elif self.end_time < now():
            # 已经结束 返回-1
            return CONTEST_ENDED
        else:
            # 正在进行 返回0
            return CONTEST_UNDERWAY

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
    total_ac_number = models.IntegerField(default=0)
    # ac 的题目才要加到这个字段里面 = ac 时间 + 错误次数 * 20 * 60
    # 没有 ac 的题目不计算罚时 单位是秒
    total_time = models.IntegerField(default=0)
    # 数据结构{23: {"is_ac": True, "ac_time": 8999, "error_number": 2, "is_first_ac": True}}
    # key 是比赛题目的id
    submission_info = JSONField(default={})

    class Meta:
        db_table = "contest_rank"

    def update_rank(self, submission):
        if not submission.contest_id or submission.contest_id != self.contest_id:
            raise ValueError("Error submission type")

        if submission.result == result["system_error"]:
            logger.warning("submission " + submission.id + " result is system error, update rank operation is ignored")
            return

        # 这道题以前提交过
        if str(submission.problem_id) in self.submission_info:
            info = self.submission_info[str(submission.problem_id)]
            # 如果这道题目已经 ac 了就跳过
            if info["is_ac"]:
                return

            self.total_submission_number += 1

            if submission.result == result["accepted"]:

                self.total_ac_number += 1

                info["is_ac"] = True
                info["ac_time"] = (submission.create_time - self.contest.start_time).total_seconds()

                # 之前已经提交过，但是是错误的，这次提交是正确的。错误的题目不计入罚时
                self.total_time += (info["ac_time"] + info["error_number"] * 20 * 60)
                problem = ContestProblem.objects.get(id=submission.problem_id)
                # 更新题目计数器在前 所以是1
                if problem.total_accepted_number == 1:
                    info["is_first_ac"] = True

            else:
                info["error_number"] += 1
                info["is_ac"] = False

        else:
            # 第一次提交这道题目
            self.total_submission_number += 1
            info = {"is_ac": False, "ac_time": 0, "error_number": 0, "is_first_ac": False}
            if submission.result == result["accepted"]:
                self.total_ac_number += 1
                info["is_ac"] = True
                info["ac_time"] = (submission.create_time - self.contest.start_time).total_seconds()
                self.total_time += info["ac_time"]
                problem = ContestProblem.objects.get(id=submission.problem_id)

                if problem.total_accepted_number == 1:
                    info["is_first_ac"] = True

            else:
                info["is_ac"] = False
                info["error_number"] = 1
        self.submission_info[str(submission.problem_id)] = info
        self.save()
