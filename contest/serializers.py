# coding=utf-8
import json
from rest_framework import serializers
from django.utils import timezone
import datetime
from account.models import User
from account.serializers import UserSerializer
from .models import Contest, ContestProblem


class CreateContestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=40)
    description = serializers.CharField(max_length=5000)
    contest_type = serializers.IntegerField()
    real_time_rank = serializers.BooleanField()
    password = serializers.CharField(max_length=30, required=False, default=None)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    groups = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    visible = serializers.BooleanField()


class DateTimeLocal(serializers.DateTimeField):
    def to_representation(self, value):
        return timezone.localtime(value)


class ContestSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["username"]

    created_by = UserSerializer()
    start_time = DateTimeLocal()
    end_time = DateTimeLocal()

    class Meta:
        model = Contest


class EditContestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=40)
    description = serializers.CharField(max_length=10000)
    contest_type = serializers.IntegerField()
    real_time_rank = serializers.BooleanField()
    password = serializers.CharField(max_length=30, required=False, default=None)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    groups = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    visible = serializers.BooleanField()


class ContestProblemSampleSerializer(serializers.ListField):
    input = serializers.CharField(max_length=3000)
    output = serializers.CharField(max_length=3000)


class JSONField(serializers.Field):
    def to_representation(self, value):
        return json.loads(value)


class CreateContestProblemSerializer(serializers.Serializer):
    contest_id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=10000)
    input_description = serializers.CharField(max_length=10000)
    output_description = serializers.CharField(max_length=10000)
    # [{"input": "1 1", "output": "2"}]
    samples = ContestProblemSampleSerializer()
    test_case_id = serializers.CharField(max_length=40)
    time_limit = serializers.IntegerField()
    memory_limit = serializers.IntegerField()
    spj = serializers.BooleanField()
    spj_language = serializers.IntegerField(required=False, default=None)
    spj_code = serializers.CharField(max_length=10000, required=False, default=None)
    hint = serializers.CharField(max_length=3000, allow_blank=True)
    score = serializers.IntegerField(required=False, default=0)
    sort_index = serializers.CharField(max_length=30)


class ContestProblemSerializer(serializers.ModelSerializer):
    class ContestSerializer(serializers.ModelSerializer):
        class Meta:
            model = Contest
            fields = ["title", "id"]

    samples = JSONField()
    contest = ContestSerializer()
    created_by = UserSerializer()

    class Meta:
        model = ContestProblem


class EditContestProblemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=10000)
    input_description = serializers.CharField(max_length=10000)
    output_description = serializers.CharField(max_length=10000)
    test_case_id = serializers.CharField(max_length=40)
    time_limit = serializers.IntegerField()
    memory_limit = serializers.IntegerField()
    spj = serializers.BooleanField()
    spj_language = serializers.IntegerField(required=False, default=None)
    spj_code = serializers.CharField(max_length=10000, required=False, default=None)
    samples = ContestProblemSampleSerializer()
    hint = serializers.CharField(max_length=3000, allow_blank=True)
    visible = serializers.BooleanField()
    sort_index = serializers.CharField(max_length=30)
    score = serializers.IntegerField(required=False, default=0)


class ContestPasswordVerifySerializer(serializers.Serializer):
    contest_id = serializers.IntegerField()
    password = serializers.CharField(max_length=30)