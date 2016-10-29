# coding=utf-8
from __future__ import unicode_literals

from django.contrib import auth
from django.core.exceptions import MultipleObjectsReturned
from django.utils.translation import ugettext as _

from utils.captcha import Captcha
from utils.otp_auth import OtpAuth
from utils.shortcuts import (APIView, )
from ..decorators import login_required
from ..models import User, UserProfile
from ..serializers import (UserLoginSerializer, UserRegisterSerializer,
                           UserChangePasswordSerializer)


class UserLoginAPIView(APIView):
    def post(self, request):
        """
        User login api
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
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
        else:
            return self.invalid_serializer(serializer)

    # todo remove this, only for debug use
    def get(self, request):
        auth.login(request, auth.authenticate(username=request.GET["username"], password=request.GET["password"]))
        return self.success({})


class UserRegisterAPIView(APIView):
    def post(self, request):
        """
        User register api
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
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
        else:
            return self.invalid_serializer(serializer)


class UserChangePasswordAPIView(APIView):
    @login_required
    def post(self, request):
        """
        User change password api
        """
        serializer = UserChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
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
        else:
            return self.invalid_serializer(serializer)
