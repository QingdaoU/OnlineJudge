from django.conf.urls import url

from ..views.admin import ProblemAPI, TestCaseUploadAPI

urlpatterns = [
    url(r"^test_case/upload$", TestCaseUploadAPI.as_view(), name="test_case_upload_api"),
    url(r"^problem$", ProblemAPI.as_view(), name="problem_api")
]
