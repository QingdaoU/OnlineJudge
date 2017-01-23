from django.conf.urls import url

from ..views.admin import UserAdminAPI

urlpatterns = [
    url(r"^user$", UserAdminAPI.as_view(), name="user_admin_api"),
]
