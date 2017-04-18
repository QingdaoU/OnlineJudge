from django.conf.urls import url

from ..views import SMTPAPI, JudgeServerAPI, WebsiteConfigAPI

urlpatterns = [
    url(r"^smtp/?$", SMTPAPI.as_view(), name="smtp_admin_api"),
    url(r"^website/?$", WebsiteConfigAPI.as_view(), name="website_config_api"),
    url(r"^judge_server/?$", JudgeServerAPI.as_view(), name="judge_server_api")
]
