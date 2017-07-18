from django.conf.urls import url

from ..views.oj import ContestAnnouncementListAPI, ContestAPI
from ..views.oj import ContestPasswordVerifyAPI

urlpatterns = [
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_api"),
    url(r"^contest/password/?$", ContestPasswordVerifyAPI.as_view(), name="contest_password_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementListAPI.as_view(), name="contest_announcement_api"),

]
