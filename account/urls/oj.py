#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from ..views.oj import (UserChangePasswordAPI, UserLoginAPI, UserRegisterAPI,
                        ApplyResetPasswordAPI, ResetPasswordAPI)

urlpatterns = [
    url(r"^login/?$", UserLoginAPI.as_view(), name="user_login_api"),
    url(r"^register/?$", UserRegisterAPI.as_view(), name="user_register_api"),
    url(r"^change_password/?$", UserChangePasswordAPI.as_view(), name="user_change_password_api"),
    url(r"^apply_reset_password/?$", ApplyResetPasswordAPI.as_view(), name="apply_reset_password_api"),
    url(r"^reset_password/?$", ResetPasswordAPI.as_view(), name="apply_reset_password_api")
]
