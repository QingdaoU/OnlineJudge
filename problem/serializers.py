from django import forms

from judge.languages import language_names, spj_language_names
from utils.api import UsernameSerializer, serializers

from .models import Problem, ProblemRuleType, ProblemTag
from .utils import parse_problem_template


class TestCaseUploadForm(forms.Form):
    spj = forms.CharField(max_length=12)
    file = forms.FileField()


class CreateSampleSerializer(serializers.Serializer):
    input = serializers.CharField(trim_whitespace=False)
    output = serializers.CharField(trim_whitespace=False)


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
    test_case_id = serializers.CharField(max_length=32)
    test_case_score = serializers.ListField(child=CreateTestCaseScoreSerializer(), allow_empty=False)
    time_limit = serializers.IntegerField(min_value=1, max_value=1000 * 60)
    memory_limit = serializers.IntegerField(min_value=1, max_value=1024)
    languages = serializers.MultipleChoiceField(choices=language_names)
    template = serializers.DictField(child=serializers.CharField(min_length=1))
    rule_type = serializers.ChoiceField(choices=[ProblemRuleType.ACM, ProblemRuleType.OI])
    spj = serializers.BooleanField()
    spj_language = serializers.ChoiceField(choices=spj_language_names, allow_blank=True, allow_null=True)
    spj_code = serializers.CharField(allow_blank=True, allow_null=True)
    spj_compile_ok = serializers.BooleanField(default=False)
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


class EditContestProblemSerializer(CreateOrEditProblemSerializer):
    id = serializers.IntegerField()
    contest_id = serializers.IntegerField()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTag
        fields = "__all__"


class CompileSPJSerializer(serializers.Serializer):
    spj_language = serializers.ChoiceField(choices=spj_language_names)
    spj_code = serializers.CharField()


class BaseProblemSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    created_by = UsernameSerializer()

    def get_public_template(self, obj):
        ret = {}
        for lang, code in obj.template.items():
            ret[lang] = parse_problem_template(code)["template"]
        return ret


class ProblemAdminSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem
        fields = "__all__"


class ProblemSerializer(BaseProblemSerializer):
    template = serializers.SerializerMethodField("get_public_template")

    class Meta:
        model = Problem
        exclude = ("test_case_score", "test_case_id", "visible", "is_public",
                   "spj_code", "spj_version", "spj_compile_ok")


class ProblemSafeSerializer(BaseProblemSerializer):
    template = serializers.SerializerMethodField("get_public_template")

    class Meta:
        model = Problem
        exclude = ("test_case_score", "test_case_id", "visible", "is_public",
                   "spj_code", "spj_version", "spj_compile_ok",
                   "difficulty", "submission_number", "accepted_number", "statistic_info")


class ContestProblemMakePublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_id = serializers.CharField(max_length=32)


class ExportProblemSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    input_description = serializers.SerializerMethodField()
    output_description = serializers.SerializerMethodField()
    test_case_score = serializers.SerializerMethodField()
    hint = serializers.SerializerMethodField()
    time_limit = serializers.SerializerMethodField()
    memory_limit = serializers.SerializerMethodField()
    spj = serializers.SerializerMethodField()
    template = serializers.SerializerMethodField()

    def get_description(self, obj):
        return {"format": "html", "value": obj.description}

    def get_input_description(self, obj):
        return {"format": "html", "value": obj.input_description}

    def get_output_description(self, obj):
        return {"format": "html", "value": obj.output_description}

    def get_hint(self, obj):
        return {"format": "html", "value": obj.hint}

    def get_test_case_score(self, obj):
        return obj.test_case_score if obj.rule_type == ProblemRuleType.OI else []

    def get_time_limit(self, obj):
        return {"unit": "ms", "value": obj.time_limit}

    def get_memory_limit(self, obj):
        return {"unit": "MB", "value": obj.memory_limit}

    def get_spj(self, obj):
        return {"enabled": obj.spj,
                "code": obj.spj_code if obj.spj else None,
                "language": obj.spj_language if obj.spj else None}

    def get_template(self, obj):
        ret = {}
        for k, v in obj.template.items():
            ret[k] = parse_problem_template(v)
        return ret

    class Meta:
        model = Problem
        fields = ("_id", "title", "description",
                  "input_description", "output_description",
                  "test_case_score", "hint", "time_limit", "memory_limit", "samples",
                  "template", "spj", "rule_type", "source", "template")


class AddContestProblemSerializer(serializers.Serializer):
    contest_id = serializers.IntegerField()
    problem_id = serializers.IntegerField()
    display_id = serializers.CharField()
