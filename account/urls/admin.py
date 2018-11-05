from django.conf.urls import url

from ..views.admin import UserAdminAPI, GenerateUserAPI, ChangeUserpasswordAPI

urlpatterns = [
    url(r"^user/?$", UserAdminAPI.as_view(), name="user_admin_api"),
    url(r"^generate_user/?$", GenerateUserAPI.as_view(), name="generate_user_api"),
    url(r"^change_userpassword/?$", ChangeUserpasswordAPI.as_view(), name="change_userpassword_api"),
]
