# coding=utf-8
from django.db import models

from account.models import User


class AbstractProblem(models.Model):

    class Meta:
        abstract = True


class Problem(AbstractProblem):
    pass


class Solution(models.Model):
    user = models.ForeignKey(User)
    problem = models.ForeignKey(Problem)