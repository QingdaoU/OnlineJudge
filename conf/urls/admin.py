from django.conf.urls import url

from ..views import SMTPAPI, JudgeServerAPI, WebsiteConfigAPI, TestCasePruneAPI, SMTPTestAPI
from ..views import CheckNewVersionAPI

urlpatterns = [
    url(r"^smtp/?$", SMTPAPI.as_view(), name="smtp_admin_api"),
    url(r"^smtp_test/?$", SMTPTestAPI.as_view(), name="smtp_test_api"),
    url(r"^website/?$", WebsiteConfigAPI.as_view(), name="website_config_api"),
    url(r"^judge_server/?$", JudgeServerAPI.as_view(), name="judge_server_api"),
    url(r"^prune_test_case/?$", TestCasePruneAPI.as_view(), name="prune_test_case_api"),
    url(r"^new_version/?$", CheckNewVersionAPI.as_view(), name="check_new_version_api"),
]
