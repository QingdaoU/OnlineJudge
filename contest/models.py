# coding=utf-8
from django.db import models

from problem.models import AbstractProblem


class Contest(models.Model):
    pass


class ContestProblem(AbstractProblem):
    contest = models.ForeignKey(Contest)
