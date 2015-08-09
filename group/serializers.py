# coding=utf-8
from rest_framework import serializers

from .models import Group


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=300)
    join_group_setting = serializers.IntegerField(min_value=0, max_value=2)


class EditGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=300)
    join_group_setting = serializers.IntegerField()


class JoinGroupRequestSerializer(serializers.Serializer):
    group = serializers.IntegerField()
    message = serializers.CharField(max_length=30)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        exclude = ["members"]