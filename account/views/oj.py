#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
from datetime import timedelta

from django.contrib import auth
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from otpauth import OtpAuth

from utils.api import APIView, validate_serializer
from utils.captcha import Captcha
from utils.shortcuts import rand_str

from ..decorators import login_required
from ..models import User, UserProfile
from ..serializers import (UserChangePasswordSerializer, UserLoginSerializer,
                           UserRegisterSerializer,
                           ApplyResetPasswordSerializer)


class UserLoginAPI(APIView):
    @validate_serializer(UserLoginSerializer)
    def post(self, request):
        """
        User login api
        """
        data = request.data
        user = auth.authenticate(username=data["username"], password=data["password"])
        # None is returned if username or password is wrong
        if user:
            if not user.two_factor_auth:
                auth.login(request, user)
                return self.success(_("Succeeded"))

            # `tfa_code` not in post data
            if user.two_factor_auth and "tfa_code" not in data:
                return self.success("tfa_required")

            if OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                auth.login(request, user)
                return self.success(_("Succeeded"))
            else:
                return self.error(_("Invalid two factor verification code"))
        else:
            return self.error(_("Invalid username or password"))

    # todo remove this, only for debug use
    def get(self, request):
        auth.login(request, auth.authenticate(username=request.GET["username"], password=request.GET["password"]))
        return self.success({})


class UserRegisterAPI(APIView):
    @validate_serializer(UserRegisterSerializer)
    def post(self, request):
        """
        User register api
        """
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error(_("Invalid captcha"))
        try:
            User.objects.get(username=data["username"])
            return self.error(_("Username already exists"))
        except User.DoesNotExist:
            pass
        try:
            User.objects.get(email=data["email"])
            return self.error(_("Email already exists"))
        # Some old data has duplicate email
        except MultipleObjectsReturned:
            return self.error(_("Email already exists"))
        except User.DoesNotExist:
            user = User.objects.create(username=data["username"], email=data["email"])
            user.set_password(data["password"])
            user.save()
            UserProfile.objects.create(user=user)
            return self.success(_("Succeeded"))


class UserChangePasswordAPI(APIView):
    @validate_serializer(UserChangePasswordSerializer)
    @login_required
    def post(self, request):
        """
        User change password api
        """
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error(_("Invalid captcha"))
        username = request.user.username
        user = auth.authenticate(username=username, password=data["old_password"])
        if user:
            user.set_password(data["new_password"])
            user.save()
            return self.success(_("Succeeded"))
        else:
            return self.error(_("Invalid old password"))


class ApplyResetPasswordAPI(APIView):
    @validate_serializer(ApplyResetPasswordSerializer)
    def post(self, request):
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error(_("Invalid captcha"))
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return self.error(_("User does not exist"))
        if user.reset_password_token_expire_time and 0 < (
            user.reset_password_token_expire_time - now()).total_seconds() < 20 * 60:
            return self.error(_("You can only reset password once per 20 minutes"))
        user.reset_password_token = rand_str()

        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        # TODO:email template
        # TODO:send email
        return self.success(_("Succeeded"))


class ResetPasswordAPI(APIView):
    def post(self, request):
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error(_("Invalid captcha"))
        try:
            user = User.objects.get(reset_password_token=data["token"])
        except User.DoesNotExist:
            return self.error(_("Token dose not exist"))
        if 0 < (user.reset_password_token_expire_time - now()).total_seconds() < 30 * 60:
            return self.error(_("Token expired"))
        user.reset_password_token = None
        user.set_password(data["password"])
        user.save()
        return self.success(_("Succeeded"))
