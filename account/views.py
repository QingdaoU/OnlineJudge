# coding=utf-8
import codecs
from django import http
from django.contrib import auth
from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, error_page, paginate, rand_str)
from utils.captcha import Captcha
from mail.tasks import send_email

from .decorators import login_required
from .models import User, UserProfile

from .serializers import (UserLoginSerializer, UserRegisterSerializer,
                          UserChangePasswordSerializer,
                          UserSerializer, EditUserSerializer,
                          ApplyResetPasswordSerializer, ResetPasswordSerializer,
                          SSOSerializer, EditUserProfileSerializer, UserProfileSerializer)

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
            captcha = Captcha(request)
            if not captcha.check(data["captcha"]):
                return error_response(u"验证码错误")
            user = auth.authenticate(username=data["username"], password=data["password"])
            # 用户名或密码错误的话 返回None
            if user:
                auth.login(request, user)
                return success_response(u"登录成功")
            else:
                return error_response(u"用户名或密码错误")
        else:
            return serializer_invalid_response(serializer)


@login_required
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
                UserProfile.objects.create(user=user, school=data["school"])
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
                return Response(status=400)
            except User.DoesNotExist:
                return Response(status=200)
        return Response(status=200)


class EmailCheckAPIView(APIView):
    def get(self, request):
        """
        检测邮箱是否存在，存在返回状态码400，不存在返回200
        ---
        """
        email = request.GET.get("email", None)
        if email:
            try:
                User.objects.get(email=email)
                return Response(status=400)
            except Exception:
                return Response(status=200)
        return Response(status=200)


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
                user = User.objects.get(username=data["username"], email=data["email"])
            except User.DoesNotExist:
                return error_response(u"用户不存在")
            if user.reset_password_token_create_time and (now() - user.reset_password_token_create_time).total_seconds() < 20 * 60:
                return error_response(u"20分钟内只能找回一次密码")
            user.reset_password_token = rand_str()
            user.reset_password_token_create_time = now()
            user.save()
            email_template = codecs.open(settings.TEMPLATES[0]["DIRS"][0] + "utils/reset_password_email.html", "r", "utf-8").read()

            email_template = email_template.replace("{{ username }}", user.username).\
                replace("{{ website_name }}", settings.WEBSITE_INFO["website_name"]).\
                replace("{{ link }}", request.scheme + "://" + request.META['HTTP_HOST'] + "/reset_password/?token=" + user.reset_password_token)

            send_email(settings.WEBSITE_INFO["website_name"],
                       user.email,
                       user.username,
                       settings.WEBSITE_INFO["website_name"] + u" 密码找回邮件",
                       email_template)
            return success_response(u"邮件发送成功")
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
                user = User.objects.get(auth_token=serializer.data["token"])
                return success_response({"username": user.username})
            except User.DoesNotExist:
                return error_response(u"用户不存在")
        else:
            return serializer_invalid_response(serializer)

    @login_required
    def get(self, request):
        callback = request.GET.get("callback", None)
        if not callback or callback != settings.SSO["callback"]:
            return error_page(request, u"参数错误")
        token = rand_str()
        request.user.auth_token = token
        request.user.save()
        return render(request, "oj/account/sso.html", {"redirect_url": callback + "?token=" + token, "callback": callback})