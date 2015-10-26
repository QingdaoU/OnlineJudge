# coding=utf-8
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView

from account.views import (UserLoginAPIView, UsernameCheckAPIView, UserRegisterAPIView,
                           UserChangePasswordAPIView, EmailCheckAPIView,
                           UserAdminAPIView, UserInfoAPIView,
                           ApplyResetPasswordAPIView, SSOAPIView)

from announcement.views import AnnouncementAdminAPIView

from contest.views import (ContestAdminAPIView, ContestProblemAdminAPIView,
                           ContestPasswordVerifyAPIView, ContestTimeAPIView)

from group.views import (GroupAdminAPIView, GroupMemberAdminAPIView,
                         JoinGroupAPIView, JoinGroupRequestAdminAPIView)

from admin.views import AdminTemplateView

from problem.views import TestCaseUploadAPIView, ProblemTagAdminAPIView, ProblemAdminAPIView
from submission.views import (SubmissionAPIView, SubmissionAdminAPIView, ContestSubmissionAPIView,
                              SubmissionShareAPIView, SubmissionRejudgeAdminAPIView,
                              ContestSubmissionAdminAPIView)
from monitor.views import QueueLengthMonitorAPIView
from utils.views import SimditorImageUploadAPIView



urlpatterns = [
    url("^$", "account.views.index_page", name="index_page"),

    url(r'^admin/$', TemplateView.as_view(template_name="admin/admin.html"), name="admin_spa_page"),
    url(r'^admin/contest/$', TemplateView.as_view(template_name="admin/contest/add_contest.html"),
        name="add_contest_page"),
    url(r'^admin/template/(?P<template_dir>\w+)/(?P<template_name>\w+).html$', AdminTemplateView.as_view(),
        name="admin_template"),

    url(r'^login/$', TemplateView.as_view(template_name="oj/account/login.html"), name="user_login_page"),
    url(r'^logout/$', "account.views.logout", name="user_logout_api"),
    url(r'^register/$', TemplateView.as_view(template_name="oj/account/register.html"),
        name="user_register_page"),
    url(r'^change_password/$', TemplateView.as_view(template_name="oj/account/change_password.html"),
        name="user_change_password_page"),
    url(r'^announcement/(?P<announcement_id>\d+)/$', "announcement.views.announcement_page",
        name="announcement_page"),

    url(r'^api/user/$', UserInfoAPIView.as_view(), name="user_info_api"),
    url(r'^api/login/$', UserLoginAPIView.as_view(), name="user_login_api"),
    url(r'^api/register/$', UserRegisterAPIView.as_view(), name="user_register_api"),
    url(r'^api/change_password/$', UserChangePasswordAPIView.as_view(), name="user_change_password_api"),
    url(r'^api/username_check/$', UsernameCheckAPIView.as_view(), name="username_check_api"),
    url(r'^api/email_check/$', EmailCheckAPIView.as_view(), name="email_check_api"),
    url(r'^api/contest/password/$', ContestPasswordVerifyAPIView.as_view(), name="contest_password_verify_api"),
    url(r'^api/contest/submission/$', ContestSubmissionAPIView.as_view(), name="contest_submission_api"),
    url(r'^api/submission/$', SubmissionAPIView.as_view(), name="submission_api"),
    url(r'^api/group_join/$', JoinGroupAPIView.as_view(), name="group_join_api"),

    url(r'^api/admin/upload_image/$', SimditorImageUploadAPIView.as_view(), name="simditor_upload_image"),
    url(r'^api/admin/announcement/$', AnnouncementAdminAPIView.as_view(), name="announcement_admin_api"),
    url(r'^api/admin/contest/$', ContestAdminAPIView.as_view(), name="contest_admin_api"),
    url(r'^api/admin/user/$', UserAdminAPIView.as_view(), name="user_admin_api"),
    url(r'^api/admin/group/$', GroupAdminAPIView.as_view(), name="group_admin_api"),
    url(r'^api/admin/group_member/$', GroupMemberAdminAPIView.as_view(), name="group_member_admin_api"),

    url(r'^api/admin/problem/$', ProblemAdminAPIView.as_view(), name="problem_admin_api"),
    url(r'^api/admin/contest_problem/$', ContestProblemAdminAPIView.as_view(), name="contest_problem_admin_api"),
    url(r'^api/admin/test_case_upload/$', TestCaseUploadAPIView.as_view(), name="test_case_upload_api"),
    url(r'^api/admin/tag/$', ProblemTagAdminAPIView.as_view(), name="problem_tag_admin_api"),
    url(r'^api/admin/join_group_request/$', JoinGroupRequestAdminAPIView.as_view(),
        name="join_group_request_admin_api"),
    url(r'^api/admin/submission/$', SubmissionAdminAPIView.as_view(), name="submission_admin_api_view"),
    url(r'^api/admin/monitor/$', QueueLengthMonitorAPIView.as_view(), name="queue_length_monitor_api"),
    url(r'^api/admin/contest_submission/$', ContestSubmissionAdminAPIView.as_view(), name="contest_submission_admin_api_view"),


    url(r'^contest/(?P<contest_id>\d+)/problem/(?P<contest_problem_id>\d+)/$', "contest.views.contest_problem_page",
        name="contest_problem_page"),
    url(r'^contest/(?P<contest_id>\d+)/problem/(?P<contest_problem_id>\d+)/submissions/$',
        "contest.views.contest_problem_my_submissions_list_page",
        name="contest_problem_my_submissions_list_page"),

    url(r'^contest/(?P<contest_id>\d+)/$', "contest.views.contest_page", name="contest_page"),
    url(r'^contest/(?P<contest_id>\d+)/problems/$', "contest.views.contest_problems_list_page",
        name="contest_problems_list_page"),
    url(r'^contest/(?P<contest_id>\d+)/submissions/$', "contest.views.contest_problem_submissions_list_page",
        name="contest_problem_submissions_list_page"),
    url(r'^contest/(?P<contest_id>\d+)/submissions/(?P<page>\d+)/$',
        "contest.views.contest_problem_submissions_list_page", name="contest_problem_submissions_list_page"),

    url(r'^contests/$', "contest.views.contest_list_page", name="contest_list_page"),
    url(r'^contests/(?P<page>\d+)/$', "contest.views.contest_list_page", name="contest_list_page"),


    url(r'^problem/(?P<problem_id>\d+)/$', "problem.views.problem_page", name="problem_page"),
    url(r'^problems/$', "problem.views.problem_list_page", name="problem_list_page"),
    url(r'^problems/(?P<page>\d+)/$', "problem.views.problem_list_page", name="problem_list_page"),
    url(r'^problem/(?P<problem_id>\d+)/submissions/$', "submission.views.problem_my_submissions_list_page",
        name="problem_my_submissions_page"),


    url(r'^submission/(?P<submission_id>\w+)/$', "submission.views.my_submission", name="my_submission_page"),
    url(r'^submissions/$', "submission.views.my_submission_list_page", name="my_submission_list_page"),
    url(r'^submissions/(?P<page>\d+)/$', "submission.views.my_submission_list_page", name="my_submission_list_page"),

    url(r'^contest/(?P<contest_id>\d+)/rank/$', "contest.views.contest_rank_page", name="contest_rank_page"),

    url(r'^groups/$', "group.views.group_list_page", name="group_list_page"),
    url(r'^groups/(?P<page>\d+)/$', "group.views.group_list_page", name="group_list_page"),
    url(r'^group/(?P<group_id>\d+)/$', "group.views.group_page", name="group_page"),
    url(r'^group/(?P<group_id>\d+)/applications/$', "group.views.application_list_page", name="group_application_page"),
    url(r'^group/application/(?P<request_id>\d+)/$', "group.views.application_page", name="group_application"),

    url(r'^about/$', TemplateView.as_view(template_name="utils/about.html"), name="about_page"),
    url(r'^help/$', TemplateView.as_view(template_name="utils/help.html"), name="help_page"),

    url(r'^api/submission/share/$', SubmissionShareAPIView.as_view(), name="submission_share_api"),

    url(r'^captcha/$', "utils.captcha.views.show_captcha", name="show_captcha"),

    url(r'^api/contest/time/$', ContestTimeAPIView.as_view(), name="contest_time_api_view"),
    url(r'^api/admin/rejudge/$', SubmissionRejudgeAdminAPIView.as_view(), name="submission_rejudge_api"),

    url(r'^user/(?P<username>.+)/$', "account.views.user_index_page"),

    url(r'^api/reset_password/$', ApplyResetPasswordAPIView.as_view(), name="apply_reset_password_api"),

    url(r'^account/settings/$', TemplateView.as_view(template_name="oj/account/settings.html"), name="account_setting_page"),
    url(r'^account/settings/avatar/$', TemplateView.as_view(template_name="oj/account/avatar.html"), name="avatar_settings_page"),
    url(r'^account/sso/$', SSOAPIView.as_view(), name="sso_api"),
]


if settings.DEBUG:
    urlpatterns.append(url(r'^docs/', include('rest_framework_swagger.urls')))