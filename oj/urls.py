# coding=utf-8
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from account.views import UserLoginAPIView, UsernameCheckAPIView, UserRegisterAPIView, UserChangePasswordAPIView
from announcement.views import AnnouncementAPIView

urlpatterns = [
    url("^$", TemplateView.as_view(template_name="oj/index.html"), name="index_page"),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^admin/$', TemplateView.as_view(template_name="admin/index.html"), name="admin_index_page"),
    url(r'^login/$', TemplateView.as_view(template_name="oj/account/login.html"), name="user_login_page"),
    url(r'^api/login/$', UserLoginAPIView.as_view(), name="user_login_api"),
    url(r'^api/register/$', UserRegisterAPIView.as_view(), name="user_register_api"),
    url(r'^api/change_password/$', UserChangePasswordAPIView.as_view(), name="user_change_password_api"),
    url(r'^api/username_check/$', UsernameCheckAPIView.as_view(), name="username_check_api"),
    url(r'^api/admin/announcement/$', AnnouncementAPIView.as_view(), name="announcement_api"),
    url(r'^problem/(?P<problem_id>\d+)/$', "problem.views.problem_page", name="problem_page"),

    url(r'^admin/contest/$', TemplateView.as_view(template_name="admin/contest/add_contest.html"), name="add_contest_page"),
    url(r'^problems/$', TemplateView.as_view(template_name="oj/problem/problem_list.html"), name="problem_list_page"),
]
