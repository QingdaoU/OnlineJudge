# coding=utf-8
from django.conf.urls import url

from ..views.oj import UserLoginAPIView, UserRegisterAPIView, UserChangePasswordAPIView

urlpatterns = [
    url(r'^login/$', UserLoginAPIView.as_view(), name="user_login_api"),
    url(r'^register/$', UserRegisterAPIView.as_view(), name="user_register_api"),
    url(r'^change_password/$', UserChangePasswordAPIView.as_view(), name="user_change_password_api")
]
