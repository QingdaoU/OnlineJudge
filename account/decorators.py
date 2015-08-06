# coding=utf-8
from django.http import HttpResponse
from django.shortcuts import render

from utils.shortcuts import error_response
from .models import User


def login_required(func):
    def check(*args, **kwargs):
        # 在class based views 里面，args 有两个元素，一个是self, 第二个才是request，
        # 在function based views 里面，args 只有request 一个参数
        request = args[-1]
        if request.user.is_authenticated():
            return func(*args, **kwargs)
        if request.is_ajax():
            return error_response(u"请先登录")
        else:
            return render(request, "utils/error.html", {"error": u"请先登录"})
    return check


def admin_required(func):
    def check(*args, **kwargs):
        request = args[-1]
        if request.user.is_authenticated() and request.user.admin_type:
            return func(*args, **kwargs)
        if request.is_ajax():
            return error_response(u"需要管理员权限")
        else:
            return render(request, "utils/error.html", {"error": "需要管理员权限"})
    return check
