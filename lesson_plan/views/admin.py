from django.db import transaction
from account.decorators import login_required, admin_role_required
from utils.api import APIView, validate_serializer
from lesson_plan.models import LessonPlan, LessonPlanProblem
from lesson_plan.serializers import (
    LessonPlanSerializer, LessonPlanDetailSerializer,
    CreateLessonPlanSerializer, UpdateLessonPlanSerializer
)
from problem.models import Problem


class LessonPlanAdminAPI(APIView):
    @admin_role_required
    def get(self, request):
        lesson_plan_id = request.GET.get("id")
        if lesson_plan_id:
            try:
                lesson_plan = LessonPlan.objects.get(id=lesson_plan_id)
                return self.success(LessonPlanDetailSerializer(lesson_plan).data)
            except LessonPlan.DoesNotExist:
                return self.error("Lesson plan does not exist")

        lesson_plans = LessonPlan.objects.all().select_related("created_by")
        keyword = request.GET.get("keyword")
        if keyword:
            lesson_plans = lesson_plans.filter(title__icontains=keyword)
        visible = request.GET.get("visible")
        if visible is not None:
            lesson_plans = lesson_plans.filter(visible=visible == "true")

        return self.success(self.paginate_data(request, lesson_plans, LessonPlanSerializer))

    @admin_role_required
    @validate_serializer(CreateLessonPlanSerializer)
    @transaction.atomic
    def post(self, request):
        data = request.data
        lesson_plan = LessonPlan.objects.create(
            title=data["title"],
            description=data.get("description", ""),
            content=data["content"],
            pdf_file=data.get("pdf_file", ""),
            cover_image=data.get("cover_image", ""),
            visible=data["visible"],
            created_by=request.user
        )

        problem_ids = data.get("problem_ids", [])
        for idx, problem_id in enumerate(problem_ids):
            try:
                problem = Problem.objects.get(id=problem_id)
                LessonPlanProblem.objects.create(
                    lesson_plan=lesson_plan,
                    problem=problem,
                    order=idx
                )
            except Problem.DoesNotExist:
                pass

        return self.success(LessonPlanDetailSerializer(lesson_plan).data)

    @admin_role_required
    @validate_serializer(UpdateLessonPlanSerializer)
    @transaction.atomic
    def put(self, request):
        lesson_plan_id = request.data.get("id")
        if not lesson_plan_id:
            return self.error("Lesson plan id is required")

        try:
            lesson_plan = LessonPlan.objects.get(id=lesson_plan_id)
        except LessonPlan.DoesNotExist:
            return self.error("Lesson plan does not exist")

        data = request.data
        if "title" in data:
            lesson_plan.title = data["title"]
        if "description" in data:
            lesson_plan.description = data["description"]
        if "content" in data:
            lesson_plan.content = data["content"]
        if "pdf_file" in data:
            lesson_plan.pdf_file = data["pdf_file"]
        if "cover_image" in data:
            lesson_plan.cover_image = data["cover_image"]
        if "visible" in data:
            lesson_plan.visible = data["visible"]
        lesson_plan.save()

        if "problem_ids" in data:
            LessonPlanProblem.objects.filter(lesson_plan=lesson_plan).delete()
            for idx, problem_id in enumerate(data["problem_ids"]):
                try:
                    problem = Problem.objects.get(id=problem_id)
                    LessonPlanProblem.objects.create(
                        lesson_plan=lesson_plan,
                        problem=problem,
                        order=idx
                    )
                except Problem.DoesNotExist:
                    pass

        return self.success(LessonPlanDetailSerializer(lesson_plan).data)

    @admin_role_required
    def delete(self, request):
        lesson_plan_id = request.GET.get("id")
        if not lesson_plan_id:
            return self.error("Lesson plan id is required")
        try:
            lesson_plan = LessonPlan.objects.get(id=lesson_plan_id)
            lesson_plan.delete()
            return self.success()
        except LessonPlan.DoesNotExist:
            return self.error("Lesson plan does not exist")
