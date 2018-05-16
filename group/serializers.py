from utils.api import serializers
from utils.api._serializers import UsernameSerializer

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()
    members = UsernameSerializer(many=True)

    class Meta:
        model = Group
        fields = "__all__"


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    password = serializers.CharField(allow_blank=True)
    allow_join = serializers.BooleanField()


class EditGroupSerializer(CreateGroupSerializer):
    id = serializers.IntegerField()


class DeleteGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    user_id = serializers.IntegerField(required=False)


class SimpleGroupSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()
    password = serializers.SerializerMethodField()
    me = serializers.BooleanField()

    def get_password(self, obj):
        return obj.password != ""

    class Meta:
        model = Group
        fields = ["id", "created_by", "name", "password", "me"]


class JoinGroupSerializer(serializers.Serializer):
    group_name = serializers.CharField()
    password = serializers.CharField(allow_blank=True)