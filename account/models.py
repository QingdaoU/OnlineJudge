# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class AdminGroup(models.Model):
    pass


class User(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    admin_group = models.ForeignKey(AdminGroup, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "user"
