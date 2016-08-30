# coding=utf-8
import os
import codecs
import qrcode
import StringIO
from django import http
from django.contrib import auth
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import MultipleObjectsReturned
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, error_page, paginate, rand_str)
from utils.captcha import Captcha
from utils.otp_auth import OtpAuth

from .tasks import _send_email

from .decorators import login_required
from .models import User, UserProfile

from .serializers import (UserLoginSerializer, UserRegisterSerializer,
                          UserChangePasswordSerializer,
                          UserSerializer, EditUserSerializer,
                          ApplyResetPasswordSerializer, ResetPasswordSerializer,
                          SSOSerializer, EditUserProfileSerializer,
                          UserProfileSerializer, TwoFactorAuthCodeSerializer)

from .decorators import super_admin_required


class UserLoginAPIView(APIView):
    def post(self, request):
        """
        用户登录json api接口
        ---
        request_serializer: UserLoginSerializer
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            user = auth.authenticate(username=data["username"], password=data["password"])
            # 用户名或密码错误的话 返回None
            if user:
                if not user.two_factor_auth:
                    auth.login(request, user)
                    return success_response(u"登录成功")

                # 没有输入两步验证的验证码
                if user.two_factor_auth and "tfa_code" not in data:
                    return success_response("tfa_required")

                if OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                    auth.login(request, user)
                    return success_response(u"登录成功")
                else:
                    return error_response(u"验证码错误")
            else:
                return error_response(u"用户名或密码错误")
        else:
            return serializer_invalid_response(serializer)


#@login_required
def logout(request):
    auth.logout(request)
    return http.HttpResponseRedirect("/")


def index_page(request):
    if not request.user.is_authenticated():
        return render(request, "oj/index.html")

    if request.META.get('HTTP_REFERER') or request.GET.get("index"):
        return render(request, "oj/index.html")
    else:
        return http.HttpResponseRedirect('/problems/')


class UserRegisterAPIView(APIView):
    def post(self, request):
        """
        用户注册json api接口
        ---
        request_serializer: UserRegisterSerializer
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            captcha = Captcha(request)
            if not captcha.check(data["captcha"]):
                return error_response(u"验证码错误")
            try:
                User.objects.get(username=data["username"])
                return error_response(u"用户名已存在")
            except User.DoesNotExist:
                pass
            try:
                User.objects.get(email=data["email"])
                return error_response(u"该邮箱已被注册，请换其他邮箱进行注册")
            # 兼容部分老数据，有邮箱重复的
            except MultipleObjectsReturned:
                return error_response(u"该邮箱已被注册，请换其他邮箱进行注册")
            except User.DoesNotExist:
                user = User.objects.create(username=data["username"], real_name=data["real_name"],
                                           email=data["email"])
                user.set_password(data["password"])
                user.save()
                UserProfile.objects.create(user=user, school=data["school"], student_id=data["student_id"])
                return success_response(u"注册成功！")
        else:
            return serializer_invalid_response(serializer)


class UserChangePasswordAPIView(APIView):
    @login_required
    def post(self, request):
        """
        用户修改密码json api接口
        ---
        request_serializer: UserChangePasswordSerializer
        """
        serializer = UserChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            captcha = Captcha(request)
            if not captcha.check(data["captcha"]):
                return error_response(u"验证码错误")
            username = request.user.username
            user = auth.authenticate(username=username, password=data["old_password"])
            if user:
                user.set_password(data["new_password"])
                user.save()
                return success_response(u"用户密码修改成功！")
            else:
                return error_response(u"密码不正确，请重新修改！")
        else:
            return serializer_invalid_response(serializer)


class UsernameCheckAPIView(APIView):
    def get(self, request):
        """
        检测用户名是否存在，存在返回状态码400，不存在返回200
        ---
        """
        username = request.GET.get("username", None)
        if username:
            try:
                User.objects.get(username=username)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)


class EmailCheckAPIView(APIView):
    def get(self, request):
        """
        检测邮箱是否存在，用状态码标识结果
        ---
        """
        # 这里是为了适应前端表单验证空间的要求
        reset = request.GET.get("reset", None)
        # 如果reset为true说明该请求是重置密码页面发出的，要返回的状态码应正好相反
        if reset:
            existed = status.HTTP_200_OK
            does_not_existed = status.HTTP_400_BAD_REQUEST
        else:
            existed = status.HTTP_400_BAD_REQUEST
            does_not_existed = status.HTTP_200_OK

        email = request.GET.get("email", None)
        if email:
            try:
                User.objects.get(email=email)
                return Response(status=existed)
            except Exception:
                return Response(status=does_not_existed)
        return Response(status=does_not_existed)


class UserAdminAPIView(APIView):
    @super_admin_required
    def put(self, request):
        """
        用户编辑json api接口
        ---
        request_serializer: EditUserSerializer
        response_serializer: UserSerializer
        """
        serializer = EditUserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                user = User.objects.get(id=data["id"])
            except User.DoesNotExist:
                return error_response(u"该用户不存在！")
            try:
                user = User.objects.get(username=data["username"])
                if user.id != data["id"]:
                    return error_response(u"昵称已经存在")
            except User.DoesNotExist:
                pass
            user.username = data["username"]
            user.real_name = data["real_name"]
            user.email = data["email"]
            user.admin_type = data["admin_type"]

            if data["password"]:
                user.set_password(data["password"])

            # 后台控制用户是否可以使用openapi
            if data["openapi"] is False:
                user.openapi_appkey = None
            elif data["openapi"] and user.openapi_appkey is None:
                user.openapi_appkey = rand_str()

            # 后台控制用户是否使用两步验证
            # 注意:用户没开启,后台开启的话,用户没有绑定过两步验证token,会造成无法登陆的!
            if data["tfa_auth"] is False:
                user.two_factor_auth = False
            elif data["tfa_auth"] and user.two_factor_auth is False:
                user.two_factor_auth = True
                user.tfa_token = rand_str()

            # 后台控制用户是否被禁用
            user.is_forbidden = data["is_forbidden"]

            user.save()
            return success_response(UserSerializer(user).data)
        else:
            return serializer_invalid_response(serializer)

    @super_admin_required
    def get(self, request):
        """
        用户分页json api接口
        ---
        response_serializer: UserSerializer
        """
        user = User.objects.all().order_by("-create_time")
        admin_type = request.GET.get("admin_type", None)
        if admin_type:
            try:
                user = user.filter(admin_type__gte=int(admin_type))
            except ValueError:
                return error_response(u"参数错误")
        keyword = request.GET.get("keyword", None)
        if keyword:
            user = user.filter(Q(username__contains=keyword) |
                               Q(real_name__contains=keyword) |
                               Q(email__contains=keyword))
        return paginate(request, user, UserSerializer)


class UserInfoAPIView(APIView):
    @login_required
    def get(self, request):
        """
        返回这个用户的个人信息
        ---
        response_serializer: UserSerializer
        """
        return success_response(UserSerializer(request.user).data)


class UserProfileAPIView(APIView):
    @login_required
    def get(self, request):
        """
        返回这个用户的个人信息
        ---
        response_serializer: UserSerializer
        """
        return success_response(UserSerializer(request.user).data)

    @login_required
    def put(self, request):
        serializer = EditUserProfileSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            user_profile = request.user.userprofile
            if data["avatar"]:
                user_profile.avatar = data["avatar"]
            else:
                user_profile.mood = data["mood"]
                user_profile.hduoj_username = data["hduoj_username"]
                user_profile.bestcoder_username = data["bestcoder_username"]
                user_profile.codeforces_username = data["codeforces_username"]
                user_profile.blog = data["blog"]
                user_profile.school = data["school"]
                user_profile.student_id = data["student_id"]
                user_profile.phone_number = data["phone_number"]
            user_profile.save()
            return success_response(u"修改成功")
        else:
            return serializer_invalid_response(serializer)


class ApplyResetPasswordAPIView(APIView):
    def post(self, request):
        """
        提交请求重置密码
        ---
        request_serializer: ApplyResetPasswordSerializer
        """
        serializer = ApplyResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            captcha = Captcha(request)
            if not captcha.check(data["captcha"]):
                return error_response(u"验证码错误")
            try:
                user = User.objects.get(email=data["email"])
            except User.DoesNotExist:
                return error_response(u"用户不存在")
            if user.reset_password_token_create_time and (
                now() - user.reset_password_token_create_time).total_seconds() < 20 * 60:
                return error_response(u"20分钟内只能找回一次密码")
            user.reset_password_token = rand_str()
            user.reset_password_token_create_time = now()
            user.save()
            email_template = codecs.open(settings.TEMPLATES[0]["DIRS"][0] + "utils/reset_password_email.html", "r",
                                         "utf-8").read()

            email_template = email_template.replace("{{ username }}", user.username). \
                replace("{{ website_name }}", settings.WEBSITE_INFO["website_name"]). \
                replace("{{ link }}", settings.WEBSITE_INFO["url"] + "/reset_password/t/" +
                        user.reset_password_token)

            _send_email.delay(settings.WEBSITE_INFO["website_name"],
                              user.email,
                              user.username,
                              settings.WEBSITE_INFO["website_name"] + u" 登录信息找回邮件",
                              email_template)
            return success_response(u"邮件发送成功,请前往您的邮箱查收")
        else:
            return serializer_invalid_response(serializer)


class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            captcha = Captcha(request)
            if not captcha.check(data["captcha"]):
                return error_response(u"验证码错误")
            try:
                user = User.objects.get(reset_password_token=data["token"])
            except User.DoesNotExist:
                return error_response(u"token 不存在")
            if (now() - user.reset_password_token_create_time).total_seconds() > 30 * 60:
                return error_response(u"token 已经过期，请在30分钟内重置密码")
            user.reset_password_token = None
            user.set_password(data["password"])
            user.save()
            return success_response(u"密码重置成功")
        else:
            return serializer_invalid_response(serializer)


def user_index_page(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return error_page(request, u"用户不存在")

    blog_link = ""

    if user.userprofile.blog:
        blog_link = user.userprofile.blog.replace("http://", "").replace("https://", "")

    return render(request, "oj/account/user_index.html", {"user": user, "blog_link": blog_link})


class SSOAPIView(APIView):
    def post(self, request):
        serializer = SSOSerializer(data=request.data)
        if serializer.is_valid():
            try:
                User.objects.get(openapi_appkey=serializer.data["appkey"])
            except User.DoesNotExist:
                return error_response(u"appkey无效")
            try:
                user = User.objects.get(auth_token=serializer.data["token"])
                user.auth_token = None
                user.save()
                return success_response({"username": user.username,
                                         "id": user.id,
                                         "admin_type": user.admin_type,
                                         "avatar": user.userprofile.avatar})
            except User.DoesNotExist:
                return error_response(u"用户不存在")
        else:
            return serializer_invalid_response(serializer)

    @login_required
    def get(self, request):
        callback = request.GET.get("callback", None)
        if not callback:
            return error_page(request, u"参数错误")
        token = rand_str()
        request.user.auth_token = token
        request.user.save()
        return render(request, "oj/account/sso.html",
                      {"redirect_url": callback + "?token=" + token, "callback": callback})


def reset_password_page(request, token):
    try:
        user = User.objects.get(reset_password_token=token)
    except User.DoesNotExist:
        return error_page(request, u"链接已失效")
    if (now() - user.reset_password_token_create_time).total_seconds() > 30 * 60:
        return error_page(request, u"链接已过期")
    return render(request, "oj/account/reset_password.html", {"user": user})


class TwoFactorAuthAPIView(APIView):
    @login_required
    def get(self, request):
        """
        获取绑定二维码
        """
        user = request.user
        if user.two_factor_auth:
            return error_response(u"已经开启两步验证了")
        token = rand_str()
        user.tfa_token = token
        user.save()

        image = qrcode.make(OtpAuth(token).to_uri("totp", settings.WEBSITE_INFO["url"], "OnlineJudgeAdmin"))
        buf = StringIO.StringIO()
        image.save(buf, 'gif')

        return HttpResponse(buf.getvalue(), 'image/gif')

    @login_required
    def post(self, request):
        """
        开启两步验证
        """
        serializer = TwoFactorAuthCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.data["code"]
            user = request.user
            if OtpAuth(user.tfa_token).valid_totp(code):
                user.two_factor_auth = True
                user.save()
                return success_response(u"开启两步验证成功")
            else:
                return error_response(u"验证码错误")
        else:
            return serializer_invalid_response(serializer)

    @login_required
    def put(self, request):
        serializer = TwoFactorAuthCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            code = serializer.data["code"]
            if OtpAuth(user.tfa_token).valid_totp(code):
                user.two_factor_auth = False
                user.save()
            else:
                return error_response(u"验证码错误")
        else:
            return serializer_invalid_response(serializer)


def user_rank_page(request, page=1):
    ranks = UserProfile.objects.filter(submission_number__gt=0).order_by("-accepted_problem_number", "-submission_number")
    paginator = Paginator(ranks, 20)
    try:
        ranks = paginator.page(int(page))
    except Exception:
        return error_page(request, u"不存在的页码")
    previous_page = next_page = None
    try:
        previous_page = ranks.previous_page_number()
    except Exception:
        pass
    try:
        next_page = ranks.next_page_number()
    except Exception:
        pass
    return render(request, "utils/rank.html", {"ranks": ranks, "page": page,
                                               "previous_page": previous_page,
                                               "next_page": next_page,
                                               "start_id": int(page) * 20 - 20,})


class AvatarUploadAPIView(APIView):
    def post(self, request):
        if "file" not in request.FILES:
            return error_response(u"文件上传失败")

        f = request.FILES["file"]
        if f.size > 1024 * 1024:
            return error_response(u"图片过大")
        if os.path.splitext(f.name)[-1].lower() not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return error_response(u"需要上传图片格式")
        name = "avatar_" + rand_str(5) + os.path.splitext(f.name)[-1]
        with open(os.path.join(settings.IMAGE_UPLOAD_DIR, name), "wb") as img:
            for chunk in request.FILES["file"]:
                img.write(chunk)
        return success_response({"path": "/static/upload/" + name})
