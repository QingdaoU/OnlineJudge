from django.conf.urls import url

from ..views.admin import TestCaseUploadAPI

urlpatterns = [
    url(r"^test_case/upload$", TestCaseUploadAPI.as_view(), name="test_case_upload_api")
]
