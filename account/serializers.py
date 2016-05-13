# coding=utf-8
from rest_framework import serializers

from .models import User, UserProfile


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)
    tfa_code = serializers.CharField(min_length=6, max_length=6, required=False)


class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=30)
    school = serializers.CharField(max_length=200, required=False, default=None)
    password = serializers.CharField(max_length=30, min_length=6)
    email = serializers.EmailField(max_length=254)
    captcha = serializers.CharField(max_length=4, min_length=4)
    student_id = serializers.CharField(max_length=15, required=False, default=None)


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(max_length=30, min_length=6)
    captcha = serializers.CharField(max_length=4, min_length=4)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "real_name", "email", "admin_type",
                  "create_time", "last_login", "two_factor_auth", "openapi_appkey", "is_forbidden"]


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30, min_length=6, required=False, default=None)
    email = serializers.EmailField(max_length=254)
    admin_type = serializers.IntegerField(default=0)
    openapi = serializers.BooleanField()
    tfa_auth = serializers.BooleanField()
    is_forbidden = serializers.BooleanField()


class ApplyResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField(max_length=4, min_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=1, max_length=40)
    password = serializers.CharField(min_length=6, max_length=30)
    captcha = serializers.CharField(max_length=4, min_length=4)


class SSOSerializer(serializers.Serializer):
    appkey = serializers.CharField(max_length=35)
    token = serializers.CharField(max_length=40)


class EditUserProfileSerializer(serializers.Serializer):
    avatar = serializers.CharField(max_length=50, required=False, default=None)
    blog = serializers.URLField(required=False, allow_blank=True, default='')
    mood = serializers.CharField(max_length=60, required=False, allow_blank=True, default='')
    hduoj_username = serializers.CharField(max_length=30, required=False, allow_blank=True, default='')
    bestcoder_username = serializers.CharField(max_length=30, required=False, allow_blank=True, default='')
    codeforces_username = serializers.CharField(max_length=30, required=False, allow_blank=True, default='')
    school = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True, default='')
    student_id = serializers.CharField(max_length=15, required=False, allow_blank=True, default="")


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ["avatar", "blog", "mood", "hduoj_username", "bestcoder_username", "codeforces_username",
                  "rank", "accepted_number", "submissions_number", "problems_status", "phone_number", "school", "student_id"]


class TwoFactorAuthCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()
