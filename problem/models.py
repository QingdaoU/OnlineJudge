from django.db import models
from jsonfield import JSONField

from account.models import User
from contest.models import Contest
from utils.models import RichTextField


class ProblemTag(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "problem_tag"


class ProblemRuleType(object):
    ACM = "ACM"
    OI = "OI"


class ProblemDifficulty(object):
    High = "High"
    Mid = "Mid"
    Low = "Low"


class AbstractProblem(models.Model):
    title = models.CharField(max_length=128)
    # HTML
    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = JSONField()
    test_case_id = models.CharField(max_length=32)
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
    rule_type = models.CharField(max_length=32)
    visible = models.BooleanField(default=True)
    difficulty = models.CharField(max_length=32)
    tags = models.ManyToManyField(ProblemTag)
    source = models.CharField(max_length=200, blank=True, null=True)
    total_submit_number = models.BigIntegerField(default=0)
    total_accepted_number = models.BigIntegerField(default=0)

    class Meta:
        db_table = "problem"
        abstract = True

    def add_submission_number(self):
        self.total_submit_number=models.F("total_submit_number") + 1
        self.save()

    def add_ac_number(self):
        self.total_accepted_number=models.F("total_accepted_number") + 1
        self.save()


class Problem(AbstractProblem):
    _id = models.CharField(max_length=24, unique=True, db_index=True)


class ContestProblem(AbstractProblem):
    _id = models.CharField(max_length=24, db_index=True)
    contest = models.ForeignKey(Contest)
    # 是否已经公开了题目，防止重复公开
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = "contest_problem"
        unique_together = (("_id", "contest"),)
