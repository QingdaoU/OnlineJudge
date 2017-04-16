#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from ..views.user import UserProfileAPI

urlpatterns = [
    url(r"^profile$", UserProfileAPI.as_view(), name="user_profile_api"),
]
