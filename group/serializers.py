# coding=utf-8
from rest_framework import serializers

from account.serializers import UserSerializer
from .models import Group, UserGroupRelation


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=300)
    join_group_setting = serializers.IntegerField(min_value=0, max_value=2)


class EditGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    name = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=300)
    join_group_setting = serializers.IntegerField()


class JoinGroupRequestSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    message = serializers.CharField(max_length=30)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        exclude = ["members"]
        
        
class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = UserGroupRelation
        exclude = ["id", "group"]
        
        
class EditGroupMemberSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    members = serializers.ListField(child=serializers.IntegerField())