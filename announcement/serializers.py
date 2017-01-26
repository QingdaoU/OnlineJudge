from account.models import User
from utils.api import serializers
from utils.api._serializers import DateTimeTZField, UsernameSerializer

from .models import Announcement


class CreateAnnouncementSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    content = serializers.CharField(max_length=10000)
    visible = serializers.BooleanField()


class AnnouncementSerializer(serializers.ModelSerializer):
    create_time = DateTimeTZField()
    last_update_time = DateTimeTZField()
    created_by = UsernameSerializer()

    class Meta:
        model = Announcement


class EditAnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    content = serializers.CharField(max_length=10000)
    visible = serializers.BooleanField()
