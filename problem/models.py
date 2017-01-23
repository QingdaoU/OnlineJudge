from django.db import models
from jsonfield import JSONField

from account.models import User
from utils.models import RichTextField


class ProblemTag(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "problem_tag"


class AbstractProblem(models.Model):
    title = models.CharField(max_length=50)
    # HTML
    description = RichTextField()
    input_description = models.CharField(max_length=10000)
    output_description = models.CharField(max_length=10000)
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = models.TextField(blank=True)
    test_case_id = models.CharField(max_length=40)
    hint = RichTextField(blank=True, null=True)
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
    spj_language = models.IntegerField(blank=True, null=True)
    spj_code = models.TextField(blank=True, null=True)
    spj_version = models.CharField(max_length=32, blank=True, null=True)
    visible = models.BooleanField(default=True)
    total_submit_number = models.IntegerField(default=0)
    total_accepted_number = models.IntegerField(default=0)

    class Meta:
        db_table = "problem"
        abstract = True

    def add_submission_number(self):
        self.accepted_problem_number = models.F("total_submit_number") + 1
        self.save()

    def add_ac_number(self):
        self.accepted_problem_number = models.F("total_accepted_number") + 1
        self.save()


class Problem(AbstractProblem):
    difficulty = models.IntegerField()
    tags = models.ManyToManyField(ProblemTag)
    source = models.CharField(max_length=200, blank=True, null=True)


class TestCaseScore(models.Model):
    test_case_id = models.CharField(max_length=32)
    score = JSONField()

    class Meta:
        db_table = "test_case_score"
