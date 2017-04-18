from django.conf.urls import url

from ..views.admin import ContestAnnouncementAPI, ContestAPI

urlpatterns = [
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementAPI.as_view(), name="contest_announcement_admin_api")
]
