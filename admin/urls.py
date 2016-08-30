from django.conf.urls import url
from .views import *
from django.views.generic import TemplateView
from utils.views import SimditorImageUploadAPIView

urlpatterns = [
    url(r'^admin/$', TemplateView.as_view(template_name="admin/admin.html"), name="admin_spa_page"),
    url(r'^admin/template/(?P<template_dir>\w+)/(?P<template_name>\w+).html$', AdminTemplateView.as_view(),
        name="admin_template"),

    url(r'^api/admin/upload_image/$', SimditorImageUploadAPIView.as_view(), name="simditor_upload_image"),
]