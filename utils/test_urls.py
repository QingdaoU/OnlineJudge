# coding=utf-8
from django.conf.urls import include, url



urlpatterns = [
    url(r'^paginate_test/$', "utils.tests.pagination_test_func"),
]

