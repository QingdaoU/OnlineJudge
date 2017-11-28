from django.conf.urls import url

from ..views.oj import ContestAnnouncementListAPI
from ..views.oj import ContestPasswordVerifyAPI, ContestAccessAPI
from ..views.oj import ContestListAPI, ContestAPI
from ..views.oj import ContestRankAPI

urlpatterns = [
    url(r"^contests/?$", ContestListAPI.as_view(), name="contest_list_api"),
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_api"),
    url(r"^contest/password/?$", ContestPasswordVerifyAPI.as_view(), name="contest_password_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementListAPI.as_view(), name="contest_announcement_api"),
    url(r"^contest/access/?$", ContestAccessAPI.as_view(), name="contest_access_api"),
    url(r"^contest_rank/?$", ContestRankAPI.as_view(), name="contest_rank_api"),
]
