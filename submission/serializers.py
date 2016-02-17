# coding=utf-8
from rest_framework import serializers

from account.models import User
from .models import Submission


class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = serializers.IntegerField()
    code = serializers.CharField(max_length=20000)


class OpenAPICreateSubmissionSerializer(serializers.Serializer):
    appkey = serializers.CharField(max_length=35)
    problem_id = serializers.IntegerField()
    language = serializers.IntegerField()
    code = serializers.CharField(max_length=20000)


class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("_get_submission_user")

    class Meta:
        model = Submission
        fields = ["id", "result", "create_time", "language", "user"]

    def _get_submission_user(self, obj):
        return User.objects.get(id=obj.user_id).username


class OpenAPISubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Submission
        fields = ["id", "result", "create_time", "language", "info"]


class SubmissionhareSerializer(serializers.Serializer):
    submission_id = serializers.CharField(max_length=40)


class SubmissionRejudgeSerializer(serializers.Serializer):
    submission_id  = serializers.CharField(max_length=40)


class CreateContestSubmissionSerializer(serializers.Serializer):
    contest_id = serializers.IntegerField()
    problem_id = serializers.IntegerField()
    language = serializers.IntegerField()
    code = serializers.CharField(max_length=20000)


