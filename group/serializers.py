# coding=utf-8
from rest_framework import serializers

from account.models import User
from account.serializers import UserSerializer
from .models import Group, UserGroupRelation, JoinGroupRequest


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=300)
    join_group_setting = serializers.IntegerField(min_value=0, max_value=2)


class EditGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    name = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=300)
    join_group_setting = serializers.IntegerField()
    visible = serializers.BooleanField()


class CreateJoinGroupRequestSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    message = serializers.CharField(max_length=30, required=False)


class JoinGroupRequestSerializer(serializers.ModelSerializer):
    class GroupSerializer(serializers.ModelSerializer):
        class Meta:
            model = Group
            fields = ["id", "name"]

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["username"]

    group = GroupSerializer()
    user = UserSerializer()

    class Meta:
        model = JoinGroupRequest


class GroupSerializer(serializers.ModelSerializer):
    members_number = serializers.SerializerMethodField("_get_group_members_number")

    def _get_group_members_number(self, group):
        return group.members.all().count()

    class Meta:
        model = Group
        exclude = ["members"]
        
        
class GroupMemberSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "username", "real_name"]

    user = UserSerializer()
    
    class Meta:
        model = UserGroupRelation
        exclude = ["id"]
        
        
class EditGroupMemberSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    members = serializers.ListField(child=serializers.IntegerField())


class PutJoinGroupRequestSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    status = serializers.BooleanField()
    
class GroupPromoteAdminSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    group_id = serializers.IntegerField()
