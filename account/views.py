# coding=utf-8
import codecs
from django import http
from django.contrib import auth
from django.shortcuts import render
from django.db.models import Q
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from utils.shortcuts import serializer_invalid_response, error_response, success_response, paginate, rand_str
from utils.captcha import Captcha
from mail.tasks import send_email

from envelopes import Envelope

from .decorators import login_required
from .models import User
from .serializers import (UserLoginSerializer, UsernameCheckSerializer,
                          UserRegisterSerializer, UserChangePasswordSerializer,
                          EmailCheckSerializer, UserSerializer, EditUserSerializer,
                          ApplyResetPasswordSerializer)
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
                # 管理员必须使用验证码 多次错误的使用验证码
                if user.admin_type > 0 or user.login_failed_counter:
                    if "captcha" not in data:
                        return error_response(u"请填写验证码！")
                    captcha = Captcha(request)
                    if not captcha.check(data["captcha"]):
                        return error_response(u"验证码错误")
                auth.login(request, user)
                # 登陆成功，计数器减去1
                if user.login_failed_counter > 0:
                    user.login_failed_counter -= 1
                    user.save()
                return success_response(u"登录成功")
            else:
                # 登陆失败，计数器加3
                try:
                    user = User.objects.get(username=data["username"])
                    user.login_failed_counter += 3
                    user.save()
                except User.DoesNotExist:
                    pass
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

    try:
        if request.META['HTTP_REFERER']:
            return render(request, "oj/index.html")
    except KeyError:
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
            except User.DoesNotExist:
                user = User.objects.create(username=data["username"], real_name=data["real_name"],
                                           email=data["email"])
                user.set_password(data["password"])
                user.save()
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
            except User.DoesNotExist:
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


class AccountSecurityAPIView(APIView):
    def get(self, request):
        """
        判断用户登录是否需要验证码
        ---
        """
        username = request.GET.get("username", None)
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return success_response({"applied_captcha": True})
            if user.admin_type > 0 or user.login_failed_counter > 0:
                return success_response({"applied_captcha": True})
        return success_response({"applied_captcha": False})


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
            user.reset_password_token = rand_str()
            user.save()
            email_template = codecs.open(settings.TEMPLATES[0]["DIRS"][0] + "utils/reset_password_email.html", "r", "utf-8").read()

            email_template = email_template.replace("{{ username }}", user.username).replace("{{ link }}", request.scheme + "://" + request.META['HTTP_HOST'] + "/reset_password/?token=" + user.reset_password_token)

            send_email(user.email, user.username, u"qduoj 密码找回邮件", email_template)
            return success_response(u"邮件发生成功")
        else:
            return serializer_invalid_response(serializer)


class ResetPasswordAPIView(APIView):
    pass


def user_index_page(request, username):
    return render(request, "oj/account/user_index.html")
