# coding=utf-8
from rest_framework import serializers



class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = serializers.IntegerField()
    code = serializers.CharField(max_length=3000)

