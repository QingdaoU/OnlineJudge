from django.conf.urls import url

from ..views import JudgeServerHeartbeatAPI, LanguagesAPI, WebsiteConfigAPI, AboutConfigAPI

urlpatterns = [
    url(r"^website/?$", WebsiteConfigAPI.as_view(), name="website_info_api"),
    url(r"^judge_server_heartbeat/?$", JudgeServerHeartbeatAPI.as_view(), name="judge_server_heartbeat_api"),
    url(r"^languages/?$", LanguagesAPI.as_view(), name="language_list_api")
]
