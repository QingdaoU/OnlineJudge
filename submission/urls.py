from django.conf.urls import url
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^problem/(?P<problem_id>\d+)/submissions/$', problem_my_submissions_list_page,
        name="problem_my_submissions_page"),
    url(r'^submission/(?P<submission_id>\w+)/$', my_submission, name="my_submission_page"),
    url(r'^submissions/$', submission_list_page, name="submission_list_page"),
    url(r'^submissions/(?P<page>\d+)/$', submission_list_page, name="my_submission_list_page"),

    url(r'^api/contest/submission/$', ContestSubmissionAPIView.as_view(), name="contest_submission_api"),
    url(r'^api/submission/$', SubmissionAPIView.as_view(), name="submission_api"),
    url(r'^api/admin/submission/$', SubmissionAdminAPIView.as_view(), name="submission_admin_api_view"),
    url(r'^api/submission/share/$', SubmissionShareAPIView.as_view(), name="submission_share_api"),
    url(r'^api/admin/rejudge/$', SubmissionRejudgeAdminAPIView.as_view(), name="submission_rejudge_api"),
    url(r'^api/open/submission/$', OpenAPISubmitCodeAPI.as_view(), name="openapi_submit_code"),

]