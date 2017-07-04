from django.conf.urls import url

from ..views.oj import (SubmissionAPI, SubmissionListAPI, SubmissionDetailAPI)

urlpatterns = [
    url(r"^submissions/?$", SubmissionAPI.as_view(), name="submission_api"),
]
