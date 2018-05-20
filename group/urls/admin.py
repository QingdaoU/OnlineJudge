from django.conf.urls import url

from ..views.admin import GroupAPI, AddUserToGroupAPI

urlpatterns = [
    url(r"^group/?$", GroupAPI.as_view(), name="group_api"),
    url(r"^group/add_user?$", AddUserToGroupAPI.as_view(), name="add_user_to_group_api"),
]
