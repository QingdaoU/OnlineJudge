from django.conf.urls import url

from ..views.user import (SSOAPI, AvatarUploadAPI, TwoFactorAuthAPI,
                          UserInfoAPI, UserProfileAPI)

urlpatterns = [
    url(r"^user/?$", UserInfoAPI.as_view(), name="user_info_api"),
    url(r"^profile/?$", UserProfileAPI.as_view(), name="user_profile_api"),
    url(r"^avatar/upload/?$", AvatarUploadAPI.as_view(), name="avatar_upload_api"),
    url(r"^sso/?$", SSOAPI.as_view(), name="sso_api"),
    url(r"^two_factor_auth/?$", TwoFactorAuthAPI.as_view(), name="two_factor_auth_api")
]
