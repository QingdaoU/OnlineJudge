# coding=utf-8
from rest_framework import serializers


class AnnouncementSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    content = serializers.CharField(max_length=10000)

