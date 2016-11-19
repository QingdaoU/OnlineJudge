import json

from django.utils import timezone

from rest_framework import serializers


class JSONField(serializers.Field):
    def to_representation(self, value):
        return json.loads(value)


class DateTimeTZField(serializers.DateTimeField):
    def to_representation(self, value):
        self.format = "%Y-%-m-%d %-H:%-M:%-S"
        value = timezone.localtime(value)
        return super(DateTimeTZField, self).to_representation(value)