from django.conf.urls import url

from ..views.oj import (SubmissionAPI, SubmissionListAPI)

urlpatterns = [
    url(r"^submission/?$", SubmissionAPI.as_view(), name="submissiob_api"),
    url(r"^submissions/?$", SubmissionListAPI.as_view(), name="submission_list_api"),
    url(r"^submissions/(?P<page>\d+)/?$", SubmissionListAPI.as_view(), name="submission_list_page_api"),
]
