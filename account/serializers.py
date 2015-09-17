# coding=utf-8
from rest_framework import serializers

from .models import User


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)
    captcha = serializers.CharField(required=False,min_length=4,max_length=4)


class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30, min_length=6)
    email = serializers.EmailField(max_length=254)
    captcha = serializers.CharField(max_length=4, min_length=4)


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(max_length=30, min_length=6)
    captcha = serializers.CharField(max_length=4, min_length=4)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ["password"]


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30, min_length=6, required=False, default=None)
    email = serializers.EmailField(max_length=254)
    admin_type = serializers.IntegerField(default=0)
