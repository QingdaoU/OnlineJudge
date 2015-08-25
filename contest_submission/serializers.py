# coding=utf-8
from rest_framework import serializers

from account.models import User


class CreateContestSubmissionSerializer(serializers.Serializer):
    contest_id = serializers.IntegerField()
    problem_id = serializers.IntegerField()
    language = serializers.IntegerField()
    code = serializers.CharField(max_length=3000)
