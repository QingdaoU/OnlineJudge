# coding=utf-8
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from account.views import UserLoginAPIView

urlpatterns = [
    url(r'^docs/', include('rest_framework_swagger.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', TemplateView.as_view(template_name="account/login.html"), name="user_login_page"),
    url(r'^api/login/$', UserLoginAPIView.as_view(), name="login_api"),
    url(r'^api/login/$', UserLoginAPIView.as_view(), name="user_login_api"),
    url(r'^problem/(?P<problem_id>\d+)/$', "problem.views.problem_page", name="problem_page"),

]
