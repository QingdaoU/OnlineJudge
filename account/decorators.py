# coding=utf-8
import urllib
import functools
from functools import wraps

from django.http import HttpResponseRedirect

from utils.shortcuts import error_response, error_page
from .models import SUPER_ADMIN, ADMIN


class BasePermissionDecorator(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        if len(args) == 2:
            self.request = args[1]
        else:
            self.request = args[0]

        if self.check_permission():
            if self.request.user.is_forbidden is True:
                if self.request.is_ajax():
                    return error_response(u"您已被禁用,请联系管理员")
                else:
                    return error_page(self.request, u"您已被禁用,请联系管理员")
            return self.func(*args, **kwargs)
        else:
            if self.request.is_ajax():
                return error_response(u"请先登录")
            else:
                return HttpResponseRedirect("/login/?__from=" + urllib.quote(self.request.path))

    def check_permission(self):
        raise NotImplementedError()


class login_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated()


class super_admin_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated() and self.request.user.admin_type == SUPER_ADMIN


class admin_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated() and self.request.user.admin_type in [SUPER_ADMIN, ADMIN]
