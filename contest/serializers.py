# coding=utf-8
import json
from rest_framework import serializers

from account.models import User
from .models import Contest, ContestProblem


class CreateContestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=40)
    description = serializers.CharField(max_length=5000)
    mode = serializers.IntegerField()
    contest_type = serializers.IntegerField()
    show_rank = serializers.BooleanField()
    show_user_submission = serializers.BooleanField()
    password = serializers.CharField(max_length=30, required=False, default=None)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    groups = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    visible = serializers.BooleanField()


class ContestSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["username"]

    created_by = UserSerializer()

    class Meta:
        model = Contest


class EditContestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=40)
    description = serializers.CharField(max_length=10000)
    mode = serializers.IntegerField()
    contest_type = serializers.IntegerField()
    show_rank = serializers.BooleanField()
    show_user_submission = serializers.BooleanField()
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
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=10000)
    input_description = serializers.CharField(max_length=10000)
    output_description = serializers.CharField(max_length=10000)
    # [{"input": "1 1", "output": "2"}]
    samples = ContestProblemSampleSerializer()
    test_case_id = serializers.CharField(max_length=40)
    time_limit = serializers.IntegerField()
    memory_limit = serializers.IntegerField()
    difficulty = serializers.IntegerField()
    hint = serializers.CharField(max_length=3000, allow_blank=True)
    sort_index = serializers.CharField(max_length=30)


class ContestProblemSerializer(serializers.ModelSerializer):
    samples = JSONField()

    class ContestSerializer(serializers.ModelSerializer):
        class Meta:
            model = Contest
            fields = ["title"]

    created_by = ContestSerializer()

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
    difficulty = serializers.IntegerField()
    samples = ContestProblemSampleSerializer()
    hint = serializers.CharField(max_length=3000, allow_blank=True)
    visible = serializers.BooleanField()
    sort_index = serializers.CharField(max_length=30)


