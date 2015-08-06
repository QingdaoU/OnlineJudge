# coding=utf-8
from django.contrib import auth
from django.shortcuts import render
from rest_framework.views import APIView

from utils.shortcuts import serializer_invalid_response, error_response, success_response

from .models import User
from .serializers import UserLoginSerializer, UsernameCheckSerializer, UserRegisterSerializer, \
    UserChangePasswordSerializer, EmailCheckSerializer


class UserLoginAPIView(APIView):
    def post(self, request):
        """
        用户登录json api接口
        ---
        request_serializer: UserLoginSerializer
        """
        serializer = UserLoginSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            user = auth.authenticate(username=data["username"], password=data["password"])
            # 用户名或密码错误的话 返回None
            if user:
                auth.login(request, user)
                return success_response(u"登录成功")
            else:
                return error_response(u"用户名或密码错误")
        else:
            return serializer_invalid_response(serializer)


class UserRegisterAPIView(APIView):
    def post(self, request):
        """
        用户注册json api接口
        ---
        request_serializer: UserRegisterSerializer
        """
        serializer = UserRegisterSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
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
    def post(self, request):
        """
        用户修改密码json api接口
        ---
        request_serializer: UserChangePasswordSerializer
        """
        serializer = UserChangePasswordSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            user = auth.authenticate(username=data["username"], password=data["old_password"])
            if user:
                user.set_password(data["new_password"])
                user.save()
                return success_response(u"用户密码修改成功！")
            else:
                return error_response(u"密码不正确，请重新修改！")
        else:
            return serializer_invalid_response(serializer)


class UsernameCheckAPIView(APIView):
    def post(self, request):
        """
        检测用户名是否存在，存在返回True，不存在返回False
        ---
        request_serializer: UsernameCheckSerializer
        """
        serializer = UsernameCheckSerializer(data=request.DATA)
        if serializer.is_valid():
            try:
                User.objects.get(username=serializer.data["username"])
                return success_response(True)
            except User.DoesNotExist:
                return success_response(False)
        else:
            return serializer_invalid_response(serializer)


class EmailCheckAPIView(APIView):
    def post(self, request):
        """
        检测邮箱是否存在，存在返回True，不存在返回False
        ---
        request_serializer: EmailCheckSerializer
        """
        serializer = EmailCheckSerializer(data=request.DATA)
        if serializer.is_valid():
            try:
                User.objects.get(email=serializer.data["email"])
                return success_response(True)
            except User.DoesNotExist:
                return success_response(False)
        else:
            return serializer_invalid_response(serializer)
