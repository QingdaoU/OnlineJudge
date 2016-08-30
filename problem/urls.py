from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^problem/(?P<problem_id>\d+)/$', problem_page, name="problem_page"),
    url(r'^problems/$', problem_list_page, name="problem_list_page"),
    url(r'^problems/(?P<page>\d+)/$', problem_list_page, name="problem_list_page"),

    url(r'^api/admin/test_case_upload/$', TestCaseUploadAPIView.as_view(), name="test_case_upload_api"),
    url(r'^api/admin/test_case_download/$', TestCaseDownloadAPIView.as_view(), name="test_case_download_api"),
    url(r'^api/admin/tag/$', ProblemTagAdminAPIView.as_view(), name="problem_tag_admin_api"),
    url(r'^api/admin/problem/$', ProblemAdminAPIView.as_view(), name="problem_admin_api"),
    url(r'^api/open/problem/$', OpenAPIProblemAPI.as_view(), name="openapi_problem_api"),

]