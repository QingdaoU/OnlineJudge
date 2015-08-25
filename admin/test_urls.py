# coding=utf-8
from django.conf.urls import include, url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^admin/$', TemplateView.as_view(template_name="admin/admin.html"), name="admin_spa_page"),
    url(r'^api/admin/test/$', "admin.tests.middleware_test_func"),
    url(r'^login/$', TemplateView.as_view(template_name="oj/account/login.html"), name="user_login_page"),
]
