from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^api/admin/judges/$', AdminJudgeServerAPIView.as_view(), name="judges_admin_api"),
]