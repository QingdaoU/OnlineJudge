from django.db import models
from utils.models import JSONField

from account.models import User
from contest.models import Contest
from utils.models import RichTextField
from utils.constants import Choices


class ProblemTag(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "problem_tag"


class ProblemRuleType(Choices):
    ACM = "ACM"
    OI = "OI"


class ProblemDifficulty(object):
    High = "High"
    Mid = "Mid"
    Low = "Low"


class Problem(models.Model):
    # display ID
    _id = models.CharField(max_length=24, db_index=True)
    contest = models.ForeignKey(Contest, null=True, blank=True)
    # for contest problem
    is_public = models.BooleanField(default=False)
    title = models.CharField(max_length=128)
    # HTML
    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = JSONField()
    test_case_id = models.CharField(max_length=32)
    # [{"input_name": "1.in", "output_name": "1.out", "score": 0}]
    test_case_score = JSONField()
    hint = RichTextField(blank=True, null=True)
    languages = JSONField()
    template = JSONField()
    create_time = models.DateTimeField(auto_now_add=True)
    # we can not use auto_now here
    last_update_time = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User)
    # ms
    time_limit = models.IntegerField()
    # MB
    memory_limit = models.IntegerField()
    # special judge related
    spj = models.BooleanField(default=False)
    spj_language = models.CharField(max_length=32, blank=True, null=True)
    spj_code = models.TextField(blank=True, null=True)
    spj_version = models.CharField(max_length=32, blank=True, null=True)
    spj_compile_ok = models.BooleanField(default=False)
    rule_type = models.CharField(max_length=32)
    visible = models.BooleanField(default=True)
    difficulty = models.CharField(max_length=32)
    tags = models.ManyToManyField(ProblemTag)
    source = models.CharField(max_length=200, blank=True, null=True)
    # for OI mode
    total_score = models.IntegerField(default=0, blank=True)
    submission_number = models.BigIntegerField(default=0)
    accepted_number = models.BigIntegerField(default=0)
    # {JudgeStatus.ACCEPTED: 3, JudgeStaus.WRONG_ANSWER: 11}, the number means count
    statistic_info = JSONField(default=dict)

    class Meta:
        db_table = "problem"
        unique_together = (("_id", "contest"),)
        ordering = ("create_time",)

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])

    def add_ac_number(self):
        self.accepted_number = models.F("accepted_number") + 1
        self.save(update_fields=["accepted_number"])
