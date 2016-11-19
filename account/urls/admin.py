from django.conf.urls import url

from ..views.admin import UserAdminAPIView

urlpatterns = [
    url(r'^user/$', UserAdminAPIView.as_view(), name="user_admin_api"),
]
