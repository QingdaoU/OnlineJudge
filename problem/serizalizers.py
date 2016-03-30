# coding=utf-8
import json

from rest_framework import serializers

from account.models import User
from .models import Problem, ProblemTag


class ProblemSampleSerializer(serializers.ListField):
    input = serializers.CharField(max_length=3000)
    output = serializers.CharField(max_length=3000)


class JSONField(serializers.Field):
    def to_representation(self, value):
        return json.loads(value)


class CreateProblemSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=10000)
    input_description = serializers.CharField(max_length=10000)
    output_description = serializers.CharField(max_length=10000)
    # [{"input": "1 1", "output": "2"}]
    samples = ProblemSampleSerializer()
    test_case_id = serializers.CharField(max_length=40)
    time_limit = serializers.IntegerField(min_value=1)
    memory_limit = serializers.IntegerField(min_value=1)
    difficulty = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.CharField(max_length=10))
    hint = serializers.CharField(max_length=3000, allow_blank=True)
    source = serializers.CharField(max_length=100, required=False, default=None)
    visible = serializers.BooleanField()


class ProblemTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTag


class BaseProblemSerializer(serializers.ModelSerializer):
    samples = JSONField()
    tags = ProblemTagSerializer(many=True)

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["username"]

    created_by = UserSerializer()


class ProblemSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem


class OpenAPIProblemSerializer(BaseProblemSerializer):

    class Meta:
        model = Problem
        exclude = ["visible", "test_case_id"]


class EditProblemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=10000)
    input_description = serializers.CharField(max_length=10000)
    output_description = serializers.CharField(max_length=10000)
    test_case_id = serializers.CharField(max_length=40)
    source = serializers.CharField(max_length=100)
    time_limit = serializers.IntegerField(min_value=1)
    memory_limit = serializers.IntegerField(min_value=1)
    difficulty = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.CharField(max_length=20))
    samples = ProblemSampleSerializer()
    hint = serializers.CharField(max_length=3000, allow_blank=True)
    visible = serializers.BooleanField()