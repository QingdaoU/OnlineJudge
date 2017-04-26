from django.conf.urls import url

from ..views import AnnouncementAdminAPI

urlpatterns = [
    url(r"^announcement/?$", AnnouncementAdminAPI.as_view(), name="announcement_admin_api"),
]
