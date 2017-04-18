from django.conf.urls import url

from ..views.oj import ContestAnnouncementListAPI

urlpatterns = [
    url(r"^contest/?$", ContestAnnouncementListAPI.as_view(), name="contest_list_api"),
]
