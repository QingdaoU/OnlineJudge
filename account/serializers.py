# coding=utf-8
from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)


class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30, min_length=6)

