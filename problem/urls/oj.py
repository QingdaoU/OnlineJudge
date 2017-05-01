from django.conf.urls import url

from ..views.oj import ProblemTagAPI, ProblemAPI

urlpatterns = [
    url(r"^problem/tags/?$", ProblemTagAPI.as_view(), name="problem_tag_list_api"),
    url(r"^problems/?$", ProblemAPI.as_view(), name="problem_list_api"),
]
