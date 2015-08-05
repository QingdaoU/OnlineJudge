# coding=utf-8
from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)


class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30, min_length=6)
    email = serializers.EmailField(max_length=254)


class UserChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    old_password = serializers.CharField(max_length=30, min_length=6)
    new_password = serializers.CharField(max_length=30, min_length=6)

