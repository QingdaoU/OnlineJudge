# coding=utf-8
from django.contrib import auth
from django.shortcuts import render
from rest_framework.views import APIView

from utils.shortcuts import serializer_invalid_response, error_response, success_response

from .models import User
from .serializers import UserLoginSerializer


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


class UserRegisterView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass
