from django.conf.urls import url

from ..views.oj import (ApplyResetPasswordAPI, ResetPasswordAPI,
                        UserChangePasswordAPI, UserRegisterAPI,
                        UserLoginAPI, UserLogoutAPI, UsernameOrEmailCheck,
                        SSOAPI, AvatarUploadAPI, TwoFactorAuthAPI, UserProfileAPI,
                        UserRankAPI)

from utils.captcha.views import CaptchaAPIView

urlpatterns = [
    url(r"^login/?$", UserLoginAPI.as_view(), name="user_login_api"),
    url(r"^logout/?$", UserLogoutAPI.as_view(), name="user_logout_api"),
    url(r"^register/?$", UserRegisterAPI.as_view(), name="user_register_api"),
    url(r"^change_password/?$", UserChangePasswordAPI.as_view(), name="user_change_password_api"),
    url(r"^apply_reset_password/?$", ApplyResetPasswordAPI.as_view(), name="apply_reset_password_api"),
    url(r"^reset_password/?$", ResetPasswordAPI.as_view(), name="apply_reset_password_api"),
    url(r"^captcha/?$", CaptchaAPIView.as_view(), name="show_captcha"),
    url(r"^check_username_or_email", UsernameOrEmailCheck.as_view(), name="check_username_or_email"),
    url(r"^profile/?$", UserProfileAPI.as_view(), name="user_profile_api"),
    url(r"^avatar/upload/?$", AvatarUploadAPI.as_view(), name="avatar_upload_api"),
    url(r"^sso/?$", SSOAPI.as_view(), name="sso_api"),
    url(r"^two_factor_auth/?$", TwoFactorAuthAPI.as_view(), name="two_factor_auth_api"),
    url(r"^user_rank/?$", UserRankAPI.as_view(), name="user_rank_api"),
]
