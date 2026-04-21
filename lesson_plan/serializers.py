from rest_framework import serializers
from .models import LessonPlan, LessonPlanProblem
from problem.serializers import ProblemSerializer


class LessonPlanSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    problems_count = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = "__all__"

    def get_problems_count(self, obj):
        return obj.lessonplanproblem_set.count()


class LessonPlanDetailSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    problems = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = "__all__"

    def get_problems(self, obj):
        lesson_plan_problems = obj.lessonplanproblem_set.all().select_related('problem')
        result = []
        for lp in lesson_plan_problems:
            problem_data = ProblemSerializer(lp.problem).data
            problem_data['order'] = lp.order
            result.append(problem_data)
        return result


class CreateLessonPlanSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField()
    pdf_file = serializers.CharField(required=False, allow_blank=True)
    cover_image = serializers.CharField(required=False, allow_blank=True)
    visible = serializers.BooleanField(default=True)
    problem_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)


class UpdateLessonPlanSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False)
    pdf_file = serializers.CharField(required=False, allow_blank=True)
    cover_image = serializers.CharField(required=False, allow_blank=True)
    visible = serializers.BooleanField(required=False)
    problem_ids = serializers.ListField(child=serializers.IntegerField(), required=False)


class LessonPlanProblemSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    order = serializers.IntegerField(default=0)
