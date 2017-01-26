import json

from django.utils import timezone
from rest_framework import serializers


class JSONField(serializers.Field):
    def to_representation(self, value):
        return json.loads(value)


class DateTimeTZField(serializers.DateTimeField):
    def to_representation(self, value):
        self.format = "%Y-%-m-%d %H:%M:%S %Z"
        value = timezone.localtime(value)
        return super(DateTimeTZField, self).to_representation(value)


class IDOnlySerializer(serializers.Serializer):
    id = serializers.IntegerField()


class UsernameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
