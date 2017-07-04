import os
from io import BytesIO

import qrcode
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from otpauth import OtpAuth

from conf.models import WebsiteConfig
from utils.api import APIView, validate_serializer, CSRFExemptAPIView
from utils.shortcuts import rand_str

from ..decorators import login_required
from ..models import User, UserProfile
from ..serializers import (SSOSerializer, TwoFactorAuthCodeSerializer,
                           UserProfileSerializer,
                           EditUserProfileSerializer, AvatarUploadForm)


class UserNameAPI(APIView):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """
        Return Username to valid login status
        """
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return self.success({
                "username": "User does not exist",
                "isLogin": False
            })
        return self.success({
            "username": user.username,
            "isLogin": True
        })


class UserProfileAPI(APIView):
    @login_required
    def get(self, request, **kwargs):
        """
        Return user info according username or user_id
        """
        username = request.GET.get("username")
        try:
            if username:
                user = User.objects.get(username=username)
            else:
                user = request.user
        except User.DoesNotExist:
            return self.error("User does not exist")
        profile = UserProfile.objects.get(user=user)
        return self.success(UserProfileSerializer(profile).data)

    @validate_serializer(EditUserProfileSerializer)
    @login_required
    def put(self, request):
        data = request.data
        user_profile = request.user.userprofile
        print(data)
        if data.get("avatar"):
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
        return self.success("Succeeded")


class AvatarUploadAPI(CSRFExemptAPIView):
    request_parsers = ()

    def post(self, request):
        form = AvatarUploadForm(request.POST, request.FILES)
        if form.is_valid():
            avatar = form.cleaned_data["file"]
        else:
            return self.error("Upload failed")
        if avatar.size > 1024 * 1024:
            return self.error("Picture too large")
        if os.path.splitext(avatar.name)[-1].lower() not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.error("Unsupported file format")

        name = "avatar_" + rand_str(5) + os.path.splitext(avatar.name)[-1]
        with open(os.path.join(settings.IMAGE_UPLOAD_DIR, name), "wb") as img:
            for chunk in avatar:
                img.write(chunk)
        print(os.path.join(settings.IMAGE_UPLOAD_DIR, name))
        return self.success({"path": "/static/upload/" + name})


class SSOAPI(APIView):
    @login_required
    def get(self, request):
        callback = request.GET.get("callback", None)
        if not callback:
            return self.error("Parameter Error")
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
            return self.error("Invalid appkey")
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
        buf = BytesIO()
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
            return self.success("Succeeded")
        else:
            return self.error("Invalid captcha")

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def put(self, request):
        code = request.data["code"]
        user = request.user
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = False
            user.save()
        else:
            return self.error("Invalid captcha")
