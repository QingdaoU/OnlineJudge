from account.decorators import login_required
from utils.api import APIView
from lesson_plan.models import LessonPlan
from lesson_plan.serializers import LessonPlanSerializer, LessonPlanDetailSerializer


class LessonPlanAPI(APIView):
    def get(self, request):
        lesson_plan_id = request.GET.get("id")
        if lesson_plan_id:
            try:
                lesson_plan = LessonPlan.objects.select_related("created_by").get(
                    id=lesson_plan_id, visible=True
                )
                return self.success(LessonPlanDetailSerializer(lesson_plan).data)
            except LessonPlan.DoesNotExist:
                return self.error("Lesson plan does not exist")

        lesson_plans = LessonPlan.objects.filter(visible=True).select_related("created_by")
        keyword = request.GET.get("keyword")
        if keyword:
            lesson_plans = lesson_plans.filter(title__icontains=keyword)

        return self.success(self.paginate_data(request, lesson_plans, LessonPlanSerializer))
