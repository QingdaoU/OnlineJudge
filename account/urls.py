from django.conf.urls import url
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    # account app
    url("^$", view = index_page, name="index_page"),
    url(r'^login/$', TemplateView.as_view(template_name="oj/account/login.html"), name="user_login_page"),
    url(r'^logout/$', logout, name="user_logout_api"),
    url(r'^register/$', TemplateView.as_view(template_name="oj/account/register.html"),
        name="user_register_page"),
    url(r'^change_password/$', TemplateView.as_view(template_name="oj/account/change_password.html"),
        name="user_change_password_page"),
    url(r'^api/user/$', UserInfoAPIView.as_view(), name="user_info_api"),
    url(r'^api/login/$', UserLoginAPIView.as_view(), name="user_login_api"),
    url(r'^api/register/$', UserRegisterAPIView.as_view(), name="user_register_api"),
    url(r'^api/change_password/$', UserChangePasswordAPIView.as_view(), name="user_change_password_api"),
    url(r'^api/username_check/$', UsernameCheckAPIView.as_view(), name="username_check_api"),
    url(r'^api/email_check/$', EmailCheckAPIView.as_view(), name="email_check_api"),
    url(r'^api/admin/user/$', UserAdminAPIView.as_view(), name="user_admin_api"),
    url(r'^api/apply_reset_password/$', ApplyResetPasswordAPIView.as_view(), name="apply_reset_password_api"),
    url(r'^api/reset_password/$', ResetPasswordAPIView.as_view(), name="apply_reset_password_api"),
    url(r'^account/settings/$', TemplateView.as_view(template_name="oj/account/settings.html"),
        name="account_setting_page"),
    url(r'^account/settings/avatar/$', TemplateView.as_view(template_name="oj/account/avatar.html"),
        name="avatar_settings_page"),
    url(r'^account/sso/$', SSOAPIView.as_view(), name="sso_api"),
    url(r'^api/account/userprofile/$', UserProfileAPIView.as_view(), name="userprofile_api"),
    url(r'^reset_password/$', TemplateView.as_view(template_name="oj/account/apply_reset_password.html"),
        name="apply_reset_password_page"),
    url(r'^reset_password/t/(?P<token>\w+)/$', reset_password_page, name="reset_password_page"),
    url(r'^api/two_factor_auth/$', TwoFactorAuthAPIView.as_view(), name="two_factor_auth_api"),
    url(r'^two_factor_auth/$', TemplateView.as_view(template_name="oj/account/two_factor_auth.html"),
        name="two_factor_auth_page"),
    url(r'^rank/(?P<page>\d+)/$', user_rank_page, name="user_rank_page"),
    url(r'^rank/$', user_rank_page, name="user_rank_page"),
    url(r'^api/avatar/upload/', AvatarUploadAPIView.as_view(), name="avatar_upload_api"),
    url(r'^user/(?P<username>.+)/$', user_index_page),
]