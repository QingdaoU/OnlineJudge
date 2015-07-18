# coding=utf-8
from django.db import models

from account.models import User
from problem.models import AbstractProblem


class Contest(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField()
    is_public = models.BooleanField()
    password = models.CharField(max_length=30, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User)


class ContestProblem(AbstractProblem):
    contest = models.ForeignKey(Contest)
