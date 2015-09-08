# coding=utf-8
from django.conf.urls import include, url
from django.views.generic import TemplateView


urlpatterns = [

    url(r'^login/$', TemplateView.as_view(template_name="oj/account/login.html"), name="user_login_page"),
]
