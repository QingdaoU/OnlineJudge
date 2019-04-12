from django.conf.urls import url

from ..views.oj import ProblemTagAPI, ProblemAPI, ContestProblemAPI, PickOneAPI, DLTestCaseAPI

urlpatterns = [
    url(r"^problem/tags/?$", ProblemTagAPI.as_view(), name="problem_tag_list_api"),
    url(r"^problem/?$", ProblemAPI.as_view(), name="problem_api"),
    url(r"^pickone/?$", PickOneAPI.as_view(), name="pick_one_api"),
    url(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_api"),
    url(r"^dl_test_case/?$", DLTestCaseAPI.as_view(), name="dl_test_case_api"),
]
