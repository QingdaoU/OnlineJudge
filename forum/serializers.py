from utils.api import serializers
from utils.api._serializers import UsernameSerializer

from .models import ForumPost, ForumReply


class CreateEditForumPostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=64)
    sort = serializers.IntegerField(min_value=0, max_value=20)
    content = serializers.CharField(max_length=1024 * 1024 * 8)
    is_top = serializers.BooleanField()
    is_nice = serializers.BooleanField()
    is_light = serializers.BooleanField()


class ForumPostSerializer(serializers.ModelSerializer):
    author = UsernameSerializer()

    class Meta:
        model = ForumPost
        fields = "__all__"


class CreateEditForumReplySerializer(serializers.Serializer):
    fa_id = serializers.IntegerField()
    content = serializers.CharField(max_length=1024 * 1024 * 8)


class ForumReplySerializer(serializers.ModelSerializer):
    author = UsernameSerializer()

    class Meta:
        model = ForumReply
        fields = "__all__"
