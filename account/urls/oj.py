from django.conf.urls import url

from ..views.oj import UserLoginAPI, UserRegisterAPI, UserChangePasswordAPI

urlpatterns = [
    url(r'^login$', UserLoginAPI.as_view(), name="user_login_api"),
    url(r'^register$', UserRegisterAPI.as_view(), name="user_register_api"),
    url(r'^change_password$', UserChangePasswordAPI.as_view(), name="user_change_password_api")
]
