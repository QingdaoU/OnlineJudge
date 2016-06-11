# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from jsonfield import JSONField


class UserManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


REGULAR_USER = 0
ADMIN = 1
SUPER_ADMIN = 2


class User(AbstractBaseUser):
    # 用户名
    username = models.CharField(max_length=30, unique=True)
    # 真实姓名
    real_name = models.CharField(max_length=30, blank=True, null=True)
    # 用户邮箱
    email = models.EmailField(max_length=254, blank=True, null=True)
    # 用户注册时间
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    # 0代表不是管理员 1是普通管理员 2是超级管理员
    admin_type = models.IntegerField(default=0)
    # JSON字典用来表示该用户的问题的解决状态 1为ac，2为正在进行
    problems_status = JSONField(default={})
    # 找回密码用的token
    reset_password_token = models.CharField(max_length=40, blank=True, null=True)
    # token 生成时间
    reset_password_token_create_time = models.DateTimeField(blank=True, null=True)
    # SSO授权token
    auth_token = models.CharField(max_length=40, blank=True, null=True)
    # 是否开启两步验证
    two_factor_auth = models.BooleanField(default=False)
    tfa_token = models.CharField(max_length=40, blank=True, null=True)
    # open api key
    openapi_appkey = models.CharField(max_length=35, blank=True, null=True)
    # 是否禁用用户
    is_forbidden = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "user"


def _random_avatar():
    import random
    return "/static/img/avatar/avatar-" + str(random.randint(1, 20)) + ".png"


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.CharField(max_length=50, default=_random_avatar)
    blog = models.URLField(blank=True, null=True)
    mood = models.CharField(max_length=200, blank=True, null=True)
    hduoj_username = models.CharField(max_length=30, blank=True, null=True)
    bestcoder_username = models.CharField(max_length=30, blank=True, null=True)
    codeforces_username = models.CharField(max_length=30, blank=True, null=True)
    accepted_problem_number = models.IntegerField(default=0)
    submission_number = models.IntegerField(default=0)
    # JSON字典用来表示该用户的问题的解决状态 1为ac，2为正在进行
    problems_status = JSONField(default={})
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    school = models.CharField(max_length=200, blank=True, null=True)
    student_id = models.CharField(max_length=15, blank=True, null=True)

    def add_accepted_problem_number(self):
        self.accepted_problem_number += 1
        self.save(update_fields=["accepted_problem_number"])

    def add_submission_number(self):
        self.submission_number += 1
        self.save(update_fields=["submission_number"])

    def minus_accepted_problem_number(self):
        self.accepted_problem_number -= 1
        self.save(update_fields=["accepted_problem_number"])

    class Meta:
        db_table = "user_profile"
