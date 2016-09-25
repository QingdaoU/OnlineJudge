# coding=utf-8
from django.conf.urls import include, url

urlpatterns = [
    url(r'^api/', include("account.urls.oj")),
    url(r'^api/admin/account/', include("account.urls.admin")),
    url(r'^api/admin/announcement/', include("announcement.urls.admin")),
]
