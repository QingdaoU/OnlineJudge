from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^announcement/(?P<announcement_id>\d+)/$', announcement_page,
        name="announcement_page"),
    url(r'^api/admin/announcement/$', AnnouncementAdminAPIView.as_view(), name="announcement_admin_api"),
]