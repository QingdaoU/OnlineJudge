from django.conf.urls import url

from ..views import AnnouncementAdminAPIView

urlpatterns = [
    url(r'^$', AnnouncementAdminAPIView.as_view(), name="announcement_admin_api"),
]
