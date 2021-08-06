from django.conf.urls import url

from ..views.admin import AnnouncementAdminAPI, AboutUsAdminAPI

urlpatterns = [
    url(r"^announcement/?$", AnnouncementAdminAPI.as_view(), name="announcement_admin_api"),
    url(r"^aboutus/?$", AboutUsAdminAPI.as_view(), name="aboutus_admin_api"),
]
