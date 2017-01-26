from django.conf.urls import url

from ..views.admin import ContestAPI

urlpatterns = [
    url(r"^contest", ContestAPI.as_view(), name="contest_api"),
]
