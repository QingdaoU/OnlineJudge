from django.conf.urls import url

from ..views.oj import AnnouncementAPI, AboutUsAPI

urlpatterns = [
    url(r"^announcement/?$", AnnouncementAPI.as_view(), name="announcement_api"),
    url(r"^aboutus/?$", AboutUsAPI.as_view(), name="aboutus_api"),
]
