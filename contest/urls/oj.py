from django.conf.urls import url

from ..views.oj import ContestAnnouncementListAPI, ContestAPI
from ..views.oj import ContestPasswordVerifyAPI, ContestAccessAPI

urlpatterns = [
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_api"),
    url(r"^contest/password/?$", ContestPasswordVerifyAPI.as_view(), name="contest_password_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementListAPI.as_view(), name="contest_announcement_api"),
    url(r"^contest/access/?$", ContestAccessAPI.as_view(), name="contest_access_api"),

]
