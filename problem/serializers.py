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
    output_name = serializers.CharField(max_length=32)
    score = serializers.IntegerField(min_value=0)


class CreateProblemCodeTemplateSerializer(serializers.Serializer):
    pass


class Difficulty(object):
    LOW = "Low"
    MID = "Mid"
    HIGH = "High"


class CreateOrEditProblemSerializer(serializers.Serializer):
    _id = serializers.CharField(max_length=32, allow_blank=True, allow_null=True)
    title = serializers.CharField(max_length=128)
    description = serializers.CharField()
    input_description = serializers.CharField()
    output_description = serializers.CharField()
    samples = serializers.ListField(child=CreateSampleSerializer(), allow_empty=False)
    test_case_id = serializers.CharField(min_length=32, max_length=32)
    test_case_score = serializers.ListField(child=CreateTestCaseScoreSerializer(), allow_empty=False)
    time_limit = serializers.IntegerField(min_value=1, max_value=1000 * 60)
    memory_limit = serializers.IntegerField(min_value=1, max_value=1024)
    languages = serializers.MultipleChoiceField(choices=language_names)
    template = serializers.DictField(child=serializers.CharField(min_length=1))
    rule_type = serializers.ChoiceField(choices=[ProblemRuleType.ACM, ProblemRuleType.OI])
    spj = serializers.BooleanField()
    spj_language = serializers.ChoiceField(choices=spj_language_names, allow_blank=True, allow_null=True)
    spj_code = serializers.CharField(allow_blank=True, allow_null=True)
    visible = serializers.BooleanField()
    difficulty = serializers.ChoiceField(choices=[Difficulty.LOW, Difficulty.MID, Difficulty.HIGH])
    tags = serializers.ListField(child=serializers.CharField(max_length=32), allow_empty=False)
    hint = serializers.CharField(allow_blank=True, allow_null=True)
    source = serializers.CharField(max_length=256, allow_blank=True, allow_null=True)


class CreateProblemSerializer(CreateOrEditProblemSerializer):
    pass


class EditProblemSerializer(CreateOrEditProblemSerializer):
    id = serializers.IntegerField()


class CreateContestProblemSerializer(CreateOrEditProblemSerializer):
    contest_id = serializers.IntegerField()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTag
        fields = "__all__"


class BaseProblemSerializer(serializers.ModelSerializer):
    samples = serializers.JSONField()
    test_case_score = serializers.JSONField()
    languages = serializers.JSONField()
    template = serializers.JSONField()
    tags = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    create_time = DateTimeTZField()
    last_update_time = DateTimeTZField()
    created_by = UsernameSerializer()
    statistic_info = serializers.JSONField()


class ProblemAdminSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem
        fields = "__all__"


class ContestProblemAdminSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem


class ProblemSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem
        exclude = ("contest", "test_case_score", "test_case_id", "visible", "is_public")


class ContestProblemSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem
        exclude = ("test_case_score", "test_case_id", "visible", "is_public")
