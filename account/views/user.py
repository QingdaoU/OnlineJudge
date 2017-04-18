import os
from io import StringIO

import qrcode
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from otpauth import OtpAuth

from conf.models import WebsiteConfig
from utils.api import APIView, validate_serializer
from utils.shortcuts import rand_str

from ..decorators import login_required
from ..models import User
from ..serializers import (EditUserSerializer, SSOSerializer,
                           TwoFactorAuthCodeSerializer, UserSerializer)


class UserInfoAPI(APIView):
    @login_required
    def get(self, request):
        """
        Return user info api
        """
        return self.success(UserSerializer(request.user).data)


class UserProfileAPI(APIView):
    @login_required
    def get(self, request):
        """
        Return user info api
        """
        return self.success(UserSerializer(request.user).data)

    @validate_serializer(EditUserSerializer)
    @login_required
    def put(self, request):
        data = request.data
        user_profile = request.user.userprofile
        if data["avatar"]:
            user_profile.avatar = data["avatar"]
        else:
            user_profile.mood = data["mood"]
            user_profile.blog = data["blog"]
            user_profile.school = data["school"]
            user_profile.student_id = data["student_id"]
            user_profile.phone_number = data["phone_number"]
            user_profile.major = data["major"]
            # Timezone & language 暂时不加
        user_profile.save()
        return self.success(_("Succeeded"))


class AvatarUploadAPI(APIView):
    def post(self, request):
        if "file" not in request.FILES:
            return self.error(_("Upload failed"))

        f = request.FILES["file"]
        if f.size > 1024 * 1024:
            return self.error(_("Picture too large"))
        if os.path.splitext(f.name)[-1].lower() not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.error(_("Unsupported file format"))

        name = "avatar_" + rand_str(5) + os.path.splitext(f.name)[-1]
        with open(os.path.join(settings.IMAGE_UPLOAD_DIR, name), "wb") as img:
            for chunk in request.FILES["file"]:
                img.write(chunk)
        return self.success({"path": "/static/upload/" + name})


class SSOAPI(APIView):
    @login_required
    def get(self, request):
        callback = request.GET.get("callback", None)
        if not callback:
            return self.error(_("Parameter Error"))
        token = rand_str()
        request.user.auth_token = token
        request.user.save()
        return self.success({"redirect_url": callback + "?token=" + token,
                             "callback": callback})

    @validate_serializer(SSOSerializer)
    def post(self, request):
        data = request.data
        try:
            User.objects.get(open_api_appkey=data["appkey"])
        except User.DoesNotExist:
            return self.error(_("Invalid appkey"))
        try:
            user = User.objects.get(auth_token=data["token"])
            user.auth_token = None
            user.save()
            return self.success({"username": user.username,
                                 "id": user.id,
                                 "admin_type": user.admin_type,
                                 "avatar": user.userprofile.avatar})
        except User.DoesNotExist:
            return self.error("User does not exist")


class TwoFactorAuthAPI(APIView):
    @login_required
    def get(self, request):
        """
        Get QR code
        """
        user = request.user
        if user.two_factor_auth:
            return self.error("Already open 2FA")
        token = rand_str()
        user.tfa_token = token
        user.save()

        config = WebsiteConfig.objects.first()
        image = qrcode.make(OtpAuth(token).to_uri("totp", config.base_url, config.name))
        buf = StringIO()
        image.save(buf, "gif")

        return HttpResponse(buf.getvalue(), "image/gif")

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def post(self, request):
        """
        Open 2FA
        """
        code = request.data["code"]
        user = request.user
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = True
            user.save()
            return self.success(_("Succeeded"))
        else:
            return self.error(_("Invalid captcha"))

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def put(self, request):
        code = request.data["code"]
        user = request.user
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = False
            user.save()
        else:
            return self.error(_("Invalid captcha"))
