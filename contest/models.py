from django.db import models
from django.utils.timezone import now
from jsonfield import JSONField

from account.models import User
from utils.models import RichTextField


class ContestType(object):
    PUBLIC_CONTEST = "Public"
    PASSWORD_PROTECTED_CONTEST = "Password Protected"


class ContestStatus(object):
    CONTEST_NOT_START = "1"
    CONTEST_ENDED = "-1"
    CONTEST_UNDERWAY = "0"


class ContestRuleType(object):
    ACM = "ACM"
    OI = "OI"


class Contest(models.Model):
    title = models.CharField(max_length=40)
    description = RichTextField()
    # show real time rank or cached rank
    real_time_rank = models.BooleanField()
    password = models.CharField(max_length=30, blank=True, null=True)
    # enum of ContestRuleType
    rule_type = models.CharField(max_length=36)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)
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

    @property
    def contest_type(self):
        if self.password:
            return ContestType.PASSWORD_PROTECTED_CONTEST
        return ContestType.PUBLIC_CONTEST

    class Meta:
        db_table = "contest"
        ordering = ("create_time",)


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
        db_table = "oi_contest_rank"


class ContestAnnouncement(models.Model):
    contest = models.ForeignKey(Contest)
    title = models.CharField(max_length=128)
    content = RichTextField()
    created_by = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contest_announcement"
