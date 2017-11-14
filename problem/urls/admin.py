from django.conf.urls import url

from ..views.admin import ContestProblemAPI, ProblemAPI, TestCaseAPI, MakeContestProblemPublicAPIView

urlpatterns = [
    url(r"^test_case/?$", TestCaseAPI.as_view(), name="test_case_api"),
    url(r"^problem/?$", ProblemAPI.as_view(), name="problem_admin_api"),
    url(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_admin_api"),
    url(r"^contest_problem/make_public/?$", MakeContestProblemPublicAPIView.as_view(), name="make_public_api"),
]
