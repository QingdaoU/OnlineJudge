from django.conf.urls import url

from ..views.admin import GroupAPI

urlpatterns = [
    url(r"^group/?$", GroupAPI.as_view(), name="group_api"),
]
