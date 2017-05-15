from django.conf.urls import url

from ..views.oj import (SubmissionAPI, SubmissionListAPI, SubmissionDetailAPI)

urlpatterns = [
    url(r"^submission/?$", SubmissionAPI.as_view(), name="submission_api"),
    url(r"^submission/(?P<submission_id>\w+)/?$", SubmissionDetailAPI.as_view(), name="submission_detail_api"),
    url(r"^submissions/?$", SubmissionListAPI.as_view(), name="submission_list_api"),
    url(r"^submissions/(?P<page>\d+)/?$", SubmissionListAPI.as_view(), name="submission_list_page_api"),
    # MyProblemSubmissionListAPI
]
