import os
import qrcode
from io import BytesIO
from datetime import timedelta
from otpauth import OtpAuth

from django.conf import settings
from django.contrib import auth
from django.utils.timezone import now
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from conf.models import WebsiteConfig
from utils.api import APIView, validate_serializer, CSRFExemptAPIView
from utils.captcha import Captcha
from utils.shortcuts import rand_str

from ..decorators import login_required
from ..models import User, UserProfile
from ..serializers import (ApplyResetPasswordSerializer, ResetPasswordSerializer,
                           UserChangePasswordSerializer, UserLoginSerializer,
                           UserRegisterSerializer, UsernameOrEmailCheckSerializer,
                           RankInfoSerializer)
from ..serializers import (SSOSerializer, TwoFactorAuthCodeSerializer,
                           UserProfileSerializer,
                           EditUserProfileSerializer, AvatarUploadForm)
from ..tasks import send_email_async


class UserProfileAPI(APIView):
    """
    判断是否登录， 若登录返回用户信息
    """

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        user = request.user
        if not user.is_authenticated():
            return self.success(0)

        username = request.GET.get("username")
        try:
            if username:
                user = User.objects.get(username=username, is_disabled=False)
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
                return self.success("Succeeded")

            # `tfa_code` not in post data
            if user.two_factor_auth and "tfa_code" not in data:
                return self.success("tfa_required")

            if OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                auth.login(request, user)
                return self.success("Succeeded")
            else:
                return self.error("Invalid two factor verification code")
        else:
            return self.error("Invalid username or password")

    # todo remove this, only for debug use
    def get(self, request):
        auth.login(request, auth.authenticate(username=request.GET["username"], password=request.GET["password"]))
        return self.success({})


class UserLogoutAPI(APIView):
    def get(self, request):
        auth.logout(request)
        return self.success({})


class UsernameOrEmailCheck(APIView):
    @validate_serializer(UsernameOrEmailCheckSerializer)
    def post(self, request):
        """
        check username or email is duplicate
        """
        data = request.data
        # True means OK.
        result = {
            "username": True,
            "email": True
        }
        if data.get("username"):
            if User.objects.filter(username=data["username"]).exists():
                result["username"] = False
        if data.get("email"):
            if User.objects.filter(email=data["email"]).exists():
                result["email"] = False
        return self.success(result)


class UserRegisterAPI(APIView):
    @validate_serializer(UserRegisterSerializer)
    def post(self, request):
        """
        User register api
        """
        data = request.data
        captcha = Captcha(request)
        if not captcha.validate(data["captcha"]):
            return self.error("Invalid captcha")
        if User.objects.filter(username=data["username"]).exists():
            return self.error("Username already exists")
        if User.objects.filter(email=data["email"]).exists():
            return self.error("Email already exists")

        user = User.objects.create(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        user.save()
        UserProfile.objects.create(user=user, time_zone=settings.USER_DEFAULT_TZ)
        return self.success("Succeeded")


class UserChangePasswordAPI(APIView):
    @validate_serializer(UserChangePasswordSerializer)
    @login_required
    def post(self, request):
        """
        User change password api
        """
        data = request.data
        captcha = Captcha(request)
        if not captcha.validate(data["captcha"]):
            return self.error("Invalid captcha")
        username = request.user.username
        user = auth.authenticate(username=username, password=data["old_password"])
        if user:
            user.set_password(data["new_password"])
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid old password")


class ApplyResetPasswordAPI(APIView):
    @validate_serializer(ApplyResetPasswordSerializer)
    def post(self, request):
        data = request.data
        captcha = Captcha(request)
        config = WebsiteConfig.objects.first()
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        if user.reset_password_token_expire_time and 0 < (
                    user.reset_password_token_expire_time - now()).total_seconds() < 20 * 60:
            return self.error("You can only reset password once per 20 minutes")
        user.reset_password_token = rand_str()

        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        email_template = open("reset_password_email.html", "w",
                              encoding="utf-8").read()
        email_template = email_template.replace("{{ username }}", user.username). \
            replace("{{ website_name }}", settings.WEBSITE_INFO["website_name"]). \
            replace("{{ link }}", settings.WEBSITE_INFO["url"] + "/reset_password/t/" +
                    user.reset_password_token)
        send_email_async.delay(config.name,
                               user.email,
                               user.username,
                               config.name + " 登录信息找回邮件",
                               email_template)
        return self.success("Succeeded")


class ResetPasswordAPI(APIView):
    @validate_serializer(ResetPasswordSerializer)
    def post(self, request):
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        try:
            user = User.objects.get(reset_password_token=data["token"])
        except User.DoesNotExist:
            return self.error("Token dose not exist")
        if 0 < (user.reset_password_token_expire_time - now()).total_seconds() < 30 * 60:
            return self.error("Token expired")
        user.reset_password_token = None
        user.set_password(data["password"])
        user.save()
        return self.success("Succeeded")


class UserRankAPI(APIView):
    def get(self, request):
        rule_type = request.GET.get("rule")
        if rule_type not in ["acm", "oi"]:
            rule_type = "acm"
        profiles = UserProfile.objects.select_related("user").filter(submission_number__gt=0)
        if rule_type == "acm":
            profiles = profiles.order_by("-accepted_number", "submission_number")
        else:
            profiles = profiles.order_by("-total_score")
        return self.success(self.paginate_data(request, profiles, RankInfoSerializer))
