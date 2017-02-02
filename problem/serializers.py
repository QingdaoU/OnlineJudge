from django import forms

from judge.languages import language_names, spj_language_names
from utils.api import DateTimeTZField, UsernameSerializer, serializers

from .models import Problem, ProblemRuleType, ProblemTag


class TestCaseUploadForm(forms.Form):
    spj = forms.CharField(max_length=12)
    file = forms.FileField()


class CreateSampleSerializer(serializers.Serializer):
    input = serializers.CharField()
    output = serializers.CharField()


class CreateTestCaseScoreSerializer(serializers.Serializer):
    input_name = serializers.CharField(max_length=32)
    score = serializers.IntegerField(min_value=0)


class Difficulty(object):
    LOW = "Low"
    MID = "Mid"
    HIGH = "High"


class CreateProblemSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    description = serializers.CharField()
    input_description = serializers.CharField()
    output_description = serializers.CharField()
    samples = serializers.ListField(child=CreateSampleSerializer())
    test_case_id = serializers.CharField(max_length=32)
    test_case_score = serializers.ListField(child=CreateTestCaseScoreSerializer())
    hint = serializers.CharField(allow_blank=True)
    time_limit = serializers.IntegerField(min_value=1, max_value=1000 * 60)
    memory_limit = serializers.IntegerField(min_value=1, max_value=1024)
    languages = serializers.ListField(child=serializers.ChoiceField(choices=language_names))
    rule_type = serializers.ChoiceField(choices=[ProblemRuleType.ACM, ProblemRuleType.OI])
    spj = serializers.BooleanField()
    spj_language = serializers.ChoiceField(choices=spj_language_names, allow_blank=True)
    spj_code = serializers.CharField(allow_blank=True)
    visible = serializers.BooleanField()
    difficulty = serializers.ChoiceField(choices=[Difficulty.LOW, Difficulty.MID, Difficulty.HIGH])
    tags = serializers.ListField(child=serializers.CharField(max_length=32))
    source = serializers.CharField(max_length=256, allow_blank=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTag


class ProblemSerializer(serializers.ModelSerializer):
    samples = serializers.JSONField()
    test_case_score = serializers.JSONField()
    languages = serializers.JSONField()
    tags = TagSerializer(many=True)
    create_time = DateTimeTZField()
    last_update_time = DateTimeTZField()
    created_by = UsernameSerializer()

    class Meta:
        model = Problem
