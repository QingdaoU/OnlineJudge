from django.conf.urls import url

from ..views.oj import SubmissionAPI, SubmissionListAPI, ContestSubmissionListAPI, SubmissionExistsAPI

urlpatterns = [
    url(r"^submission/?$", SubmissionAPI.as_view(), name="submission_api"),
    url(r"^submissions/?$", SubmissionListAPI.as_view(), name="submission_list_api"),
    url(r"^submission_exists/?$", SubmissionExistsAPI.as_view(), name="submission_exists"),
    url(r"^contest_submissions/?$", ContestSubmissionListAPI.as_view(), name="contest_submission_list_api"),
]
