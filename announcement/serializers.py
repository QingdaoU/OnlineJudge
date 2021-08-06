from utils.api import serializers
from utils.api._serializers import UsernameSerializer

from .models import Announcement, AboutUs


class CreateAnnouncementSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=64)
    content = serializers.CharField(max_length=1024 * 1024 * 8)
    visible = serializers.BooleanField()


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()

    class Meta:
        model = Announcement
        fields = "__all__"


class EditAnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=64)
    content = serializers.CharField(max_length=1024 * 1024 * 8)
    visible = serializers.BooleanField()


class CreateAboutUsSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=1024 * 1024 * 8)


class AboutUsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AboutUs
        fields = "__all__"


class EditAboutUsSerializer(serializers.Serializer):
    id = 0
    content = serializers.CharField(max_length=1024 * 1024 * 8)
