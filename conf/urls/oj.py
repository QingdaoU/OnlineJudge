from django.conf.urls import url

from ..views import JudgeServerHeartbeatAPI, WebsiteConfigAPI

urlpatterns = [
    url(r"^website$", WebsiteConfigAPI.as_view(), name="website_info_api"),
    url(r"^judge_server_heartbeat$", JudgeServerHeartbeatAPI.as_view(), name="judge_server_heartbeat_api")
]
