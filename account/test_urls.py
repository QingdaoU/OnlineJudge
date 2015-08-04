# coding=utf-8
from django.conf.urls import include, url

from .tests import LoginRequiredCBVTestWithArgs, LoginRequiredCBVTestWithoutArgs


urlpatterns = [
    url(r'^test/fbv/1/$', "account.tests.login_required_FBV_test_without_args"),
    url(r'^test/fbv/(?P<problem_id>\d+)/$', "account.tests.login_required_FBC_test_with_args"),
    url(r'^test/cbv/1/$', LoginRequiredCBVTestWithoutArgs.as_view()),
    url(r'^test/cbv/(?P<problem_id>\d+)/$', LoginRequiredCBVTestWithArgs.as_view()),
]
