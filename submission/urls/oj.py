from django.conf.urls import url

from ..views.oj import SubmissionAPI, SubmissionListAPI

urlpatterns = [
    url(r"^submission/?$", SubmissionAPI.as_view(), name="submission_api"),
    url(r"^submissions/?$", SubmissionListAPI.as_view(), name="submission_list_api"),
]
