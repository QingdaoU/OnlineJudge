# coding=utf-8
from django.conf.urls import include, url
from django.views.generic import TemplateView

from .tests import (LoginRequiredCBVTestWithArgs, LoginRequiredCBVTestWithoutArgs,
                    AdminRequiredCBVTestWithArgs, AdminRequiredCBVTestWithoutArgs)


urlpatterns = [
    url(r'^login_required_test/fbv/1/$', "account.tests.login_required_FBV_test_without_args"),
    url(r'^login_required_test/fbv/(?P<problem_id>\d+)/$', "account.tests.login_required_FBC_test_with_args"),
    url(r'^login_required_test/cbv/1/$', LoginRequiredCBVTestWithoutArgs.as_view()),
    url(r'^login_required_test/cbv/(?P<problem_id>\d+)/$', LoginRequiredCBVTestWithArgs.as_view()),
    
    url(r'^admin_required_test/fbv/1/$', "account.tests.admin_required_FBV_test_without_args"),
    url(r'^admin_required_test/fbv/(?P<problem_id>\d+)/$', "account.tests.admin_required_FBC_test_with_args"),
    url(r'^admin_required_test/cbv/1/$', AdminRequiredCBVTestWithoutArgs.as_view()),
    url(r'^admin_required_test/cbv/(?P<problem_id>\d+)/$', AdminRequiredCBVTestWithArgs.as_view()),
    url(r'^login/$', TemplateView.as_view(template_name="oj/account/login.html"), name="user_login_page"),
]
