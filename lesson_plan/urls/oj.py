from django.conf.urls import url
from ..views.oj import LessonPlanAPI

urlpatterns = [
    url(r"^lesson_plan/?$", LessonPlanAPI.as_view(), name="lesson_plan_api"),
]
