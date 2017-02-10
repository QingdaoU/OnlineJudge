from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from jsonfield import JSONField


class AdminType(object):
    REGULAR_USER = "Regular User"
    ADMIN = "Admin"
    SUPER_ADMIN = "Super Admin"


class ProblemSolutionStatus(object):
    ACCEPTED = 1
    PENDING = 2


class ProblemPermission(object):
    NONE = "None"
    OWN = "Own"
    ALL = "All"


class UserManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class User(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    real_name = models.CharField(max_length=30, null=True)
    email = models.EmailField(max_length=254, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    # One of UserType
    admin_type = models.CharField(max_length=24, default=AdminType.REGULAR_USER)
    problem_permission = models.CharField(max_length=24, default=ProblemPermission.NONE)
    reset_password_token = models.CharField(max_length=40, null=True)
    reset_password_token_expire_time = models.DateTimeField(null=True)
    # SSO auth token
    auth_token = models.CharField(max_length=40, null=True)
    two_factor_auth = models.BooleanField(default=False)
    tfa_token = models.CharField(max_length=40, null=True)
    # open api key
    open_api = models.BooleanField(default=False)
    open_api_appkey = models.CharField(max_length=35, null=True)
    is_disabled = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def is_super_admin(self):
        return self.admin_type == AdminType.SUPER_ADMIN

    def is_admin_role(self):
        return self.admin_type in [AdminType.ADMIN, AdminType.SUPER_ADMIN]

    def can_mgmt_all_problem(self):
        return self.problem_permission == ProblemPermission.ALL

    class Meta:
        db_table = "user"


def _random_avatar():
    import random
    return "/static/img/avatar/avatar-" + str(random.randint(1, 20)) + ".png"


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # Store user problem solution status with json string format
    # {"problems": {1: ProblemSolutionStatus.ACCEPTED}, "contest_problems": {20: ProblemSolutionStatus.PENDING)}
    problems_status = JSONField(default={})
    avatar = models.CharField(max_length=50, default=_random_avatar)
    blog = models.URLField(blank=True, null=True)
    mood = models.CharField(max_length=200, blank=True, null=True)
    accepted_problem_number = models.IntegerField(default=0)
    submission_number = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    school = models.CharField(max_length=200, blank=True, null=True)
    major = models.CharField(max_length=200, blank=True, null=True)
    student_id = models.CharField(max_length=15, blank=True, null=True)
    time_zone = models.CharField(max_length=32, blank=True, null=True)
    language = models.CharField(max_length=32, blank=True, null=True)

    def add_accepted_problem_number(self):
        self.accepted_problem_number = models.F("accepted_problem_number") + 1
        self.save()

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save()

    def minus_accepted_problem_number(self):
        self.accepted_problem_number = models.F("accepted_problem_number") - 1
        self.save()

    class Meta:
        db_table = "user_profile"
