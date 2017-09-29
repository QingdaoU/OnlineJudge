import os
import qrcode
import pickle
from datetime import timedelta
from otpauth import OtpAuth

from django.conf import settings
from django.contrib import auth
from importlib import import_module
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string

from conf.models import WebsiteConfig
from utils.api import APIView, validate_serializer
from utils.captcha import Captcha
from utils.shortcuts import rand_str, img2base64, timestamp2utcstr
from utils.cache import default_cache
from utils.constants import CacheKey

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
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        """
        判断是否登录， 若登录返回用户信息
        """
        user = request.user
        if not user.is_authenticated():
            return self.success({})
        username = request.GET.get("username")
        try:
            if username:
                user = User.objects.get(username=username, is_disabled=False)
            else:
                user = request.user
        except User.DoesNotExist:
            return self.error("User does not exist")
        profile = UserProfile.objects.select_related("user").get(user=user)
        return self.success(UserProfileSerializer(profile).data)

    @validate_serializer(EditUserProfileSerializer)
    @login_required
    def put(self, request):
        data = request.data
        user_profile = request.user.userprofile
        for k, v in data.items():
            setattr(user_profile, k, v)
        user_profile.save()
        return self.success(UserProfileSerializer(user_profile).data)


class AvatarUploadAPI(APIView):
    request_parsers = ()

    @login_required
    def post(self, request):
        form = AvatarUploadForm(request.POST, request.FILES)
        if form.is_valid():
            avatar = form.cleaned_data["file"]
        else:
            return self.error("Invalid file content")
        # 2097152 = 2 * 1024 * 1024 = 2MB
        if avatar.size > 2097152:
            return self.error("Picture is too large")
        suffix = os.path.splitext(avatar.name)[-1].lower()
        if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.error("Unsupported file format")

        name = rand_str(10) + suffix
        with open(os.path.join(settings.IMAGE_UPLOAD_DIR_ABS, name), "wb") as img:
            for chunk in avatar:
                img.write(chunk)
        user_profile = request.user.userprofile
        _, old_avatar = os.path.split(user_profile.avatar)
        if old_avatar != "default.png":
            os.remove(os.path.join(settings.IMAGE_UPLOAD_DIR_ABS, old_avatar))

        user_profile.avatar = f"/{settings.IMAGE_UPLOAD_DIR}/{name}"
        user_profile.save()
        return self.success("Succeeded")


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
        label = f"{config.name_shortcut}:{user.username}"
        image = qrcode.make(OtpAuth(token).to_uri("totp", label, config.name))
        return self.success(img2base64(image))

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
            return self.error("Invalid code")

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def put(self, request):
        code = request.data["code"]
        user = request.user
        if not user.two_factor_auth:
            return self.error("Other session have disabled TFA")
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = False
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid code")


class CheckTFARequiredAPI(APIView):
    @validate_serializer(UsernameOrEmailCheckSerializer)
    def post(self, request):
        """
        Check TFA is required
        """
        data = request.data
        result = False
        if data.get("username"):
            try:
                user = User.objects.get(username=data["username"])
                result = user.two_factor_auth
            except User.DoesNotExist:
                pass
        return self.success({"result": result})


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
            if user.is_disabled:
                return self.error("Your account have been disabled")
            if not user.two_factor_auth:
                auth.login(request, user)
                return self.success("Succeeded")

            # `tfa_code` not in post data
            if user.two_factor_auth and "tfa_code" not in data:
                return self.error("tfa_required")

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
        # True means already exist.
        result = {
            "username": False,
            "email": False
        }
        if data.get("username"):
            if User.objects.filter(username=data["username"]).exists():
                result["username"] = True
        if data.get("email"):
            if User.objects.filter(email=data["email"]).exists():
                result["email"] = True
        return self.success(result)


class UserRegisterAPI(APIView):
    @validate_serializer(UserRegisterSerializer)
    def post(self, request):
        """
        User register api
        """
        config = default_cache.get(CacheKey.website_config)
        if config:
            config = pickle.loads(config)
        else:
            config = WebsiteConfig.objects.first()
            if not config:
                config = WebsiteConfig.objects.create()
            default_cache.set(CacheKey.website_config, pickle.dumps(config))

        if not config.allow_register:
            return self.error("Register have been disabled by admin")

        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        if User.objects.filter(username=data["username"]).exists():
            return self.error("Username already exists")
        if User.objects.filter(email=data["email"]).exists():
            return self.error("Email already exists")

        user = User.objects.create(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        user.save()
        UserProfile.objects.create(user=user)
        return self.success("Succeeded")


class UserChangePasswordAPI(APIView):
    @validate_serializer(UserChangePasswordSerializer)
    @login_required
    def post(self, request):
        """
        User change password api
        """
        data = request.data
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
        if user.reset_password_token_expire_time and 0 < int(
                (user.reset_password_token_expire_time - now()).total_seconds()) < 20 * 60:
            return self.error("You can only reset password once per 20 minutes")
        user.reset_password_token = rand_str()
        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        render_data = {
            "username": user.username,
            "website_name": config.name,
            "link": f"{config.base_url}/reset-password/{user.reset_password_token}"
        }
        email_html = render_to_string("reset_password_email.html", render_data)
        send_email_async.delay(config.name,
                               user.email,
                               user.username,
                               config.name + " 登录信息找回邮件",
                               email_html)
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
        if int((user.reset_password_token_expire_time - now()).total_seconds()) < 0:
            return self.error("Token have expired")
        user.reset_password_token = None
        user.two_factor_auth = False
        user.set_password(data["password"])
        user.save()
        return self.success("Succeeded")


class SessionManagementAPI(APIView):
    @login_required
    def get(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        SessionStore = engine.SessionStore
        current_session = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        current_session = request.session.session_key
        session_keys = request.user.session_keys
        result = []
        modified = False
        for key in session_keys[:]:
            session = SessionStore(key)
            # session does not exist or is expiry
            if not session._session:
                session_keys.remove(key)
                modified = True
                continue

            s = {}
            if current_session == key:
                s["current_session"] = True
            s["ip"] = session["ip"]
            s["user_agent"] = session["user_agent"]
            s["last_activity"] = timestamp2utcstr(session["last_activity"])
            s["session_key"] = key
            result.append(s)
        if modified:
            request.user.save()
        return self.success(result)

    @login_required
    def delete(self, request):
        session_key = request.GET.get("session_key")
        if not session_key:
            return self.error("Parameter Error")
        request.session.delete(session_key)
        if session_key in request.user.session_keys:
            request.user.session_keys.remove(session_key)
            request.user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid session_key")


class UserRankAPI(APIView):
    def get(self, request):
        rule_type = request.GET.get("rule")
        if rule_type not in ["acm", "oi"]:
            rule_type = "acm"
        profiles = UserProfile.objects.select_related("user")\
            .filter(submission_number__gt=0)\
            .exclude(user__is_disabled=True)
        if rule_type == "acm":
            profiles = profiles.order_by("-accepted_number", "submission_number")
        else:
            profiles = profiles.order_by("-total_score")
        return self.success(self.paginate_data(request, profiles, RankInfoSerializer))
