# coding=utf-8
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from account.views import UserLoginAPIView

urlpatterns = [
    url("^$", TemplateView.as_view(template_name="oj/index.html"), name="index_page"),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^admin/$', TemplateView.as_view(template_name="admin/index.html"), name="admin_index_page"),
    url(r'^login/$', TemplateView.as_view(template_name="oj/account/login.html"), name="user_login_page"),
    url(r'^register/$', TemplateView.as_view(template_name="oj/account/register.html"), name="user_register_page"),
    url(r'^change_password/$', TemplateView.as_view(template_name="oj/account/change_password.html"), name="user_change_password_page"),
    url(r'^api/login/$', UserLoginAPIView.as_view(), name="login_api"),
    url(r'^api/login/$', UserLoginAPIView.as_view(), name="user_login_api"),
    url(r'^problem/(?P<problem_id>\d+)/$', "problem.views.problem_page", name="problem_page"),

    url(r'^admin/contest/$', TemplateView.as_view(template_name="admin/contest/add_contest.html"), name="add_contest_page"),
    url(r'^problems/$', TemplateView.as_view(template_name="oj/problem/problem_list.html"), name="problem_list_page"),
]
