from django.conf.urls import url

from ..views import SMTPAPI, JudgeServerAPI, WebsiteConfigAPI, TestCasePruneAPI, SMTPTestAPI
from ..views import ReleaseNotesAPI, DashboardInfoAPI

urlpatterns = [
    url(r"^smtp/?$", SMTPAPI.as_view(), name="smtp_admin_api"),
    url(r"^smtp_test/?$", SMTPTestAPI.as_view(), name="smtp_test_api"),
    url(r"^website/?$", WebsiteConfigAPI.as_view(), name="website_config_api"),
    url(r"^judge_server/?$", JudgeServerAPI.as_view(), name="judge_server_api"),
    url(r"^prune_test_case/?$", TestCasePruneAPI.as_view(), name="prune_test_case_api"),
    url(r"^versions/?$", ReleaseNotesAPI.as_view(), name="get_release_notes_api"),
    url(r"^dashboard_info", DashboardInfoAPI.as_view(), name="dashboard_info_api"),
]
