from django.conf.urls import url

from ..views.oj import ContestAnnouncementListAPI, ContestListAPI

urlpatterns = [
    url(r"^contest/?$", ContestListAPI.as_view(), name="contest_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementListAPI.as_view(), name="contest_announcement_api"),

]
