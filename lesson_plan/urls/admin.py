from django.conf.urls import url
from ..views.admin import LessonPlanAdminAPI

urlpatterns = [
    url(r"^lesson_plan/?$", LessonPlanAdminAPI.as_view(), name="lesson_plan_admin_api"),
]
