from django.conf.urls import url

from ..views.oj import ProblemTagAPI

urlpatterns = [
    url(r"^problem/tags/?$", ProblemTagAPI.as_view(), name="problem_tag_list_api")
]
