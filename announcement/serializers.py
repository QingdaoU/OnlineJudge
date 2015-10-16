# coding=utf-8
from rest_framework import serializers

from account.models import User
from .models import Announcement


class CreateAnnouncementSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    content = serializers.CharField(max_length=10000)


class AnnouncementSerializer(serializers.ModelSerializer):

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["username"]

    created_by = UserSerializer()

    class Meta:
        model = Announcement


class EditAnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    content = serializers.CharField(max_length=10000)
    visible = serializers.BooleanField()