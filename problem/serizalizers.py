# coding=utf-8
import json

from rest_framework import serializers

from account.models import User
from .models import Problem


class ProblemSampleSerializer(serializers.ListField):
    input = serializers.CharField(max_length=3000)
    output = serializers.CharField(max_length=3000)


class JSONField(serializers.Field):
    def to_representation(self, value):
        print value, type(value)
        return json.loads(value)


class CreateProblemSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=10000)
    # [{"input": "1 1", "output": "2"}]
    sample = ProblemSampleSerializer()
    test_case_id = serializers.CharField(max_length=40)
    source = serializers.CharField(max_length=30, required=False, default=None)
    time_limit = serializers.IntegerField()
    memory_limit = serializers.IntegerField()
    difficulty = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.IntegerField())
    hint = serializers.CharField(max_length=3000, required=False, default=None)


class ProblemSerializer(serializers.ModelSerializer):
    sample = JSONField()

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["username"]

    created_by = UserSerializer()

    class Meta:
        model = Problem


class EditProblemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=10000)
    test_case_id = serializers.CharField(max_length=40)
    source = serializers.CharField(max_length=30)
    time_limit = serializers.IntegerField()
    memory_limit = serializers.IntegerField()
    difficulty = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.IntegerField())
    sample = ProblemSampleSerializer()
    hint = serializers.CharField(max_length=10000)
    visible = serializers.BooleanField()

