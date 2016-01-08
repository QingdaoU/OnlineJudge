# coding=utf-8
import urllib
import functools

from django.http import HttpResponseRedirect

from rest_framework import permissions

from utils.shortcuts import error_response
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
            return self.func(*args, **kwargs)
        else:
            if self.request.is_ajax():
                return error_response(u"请先登录")
            else:
                return HttpResponseRedirect("/login/?__from=" + urllib.quote(self.request.build_absolute_uri()))

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


# Permission check for RESTful view

class LoginRequired(permissions.BasePermission):
    def has_permission(self, request, view):
        return self.request.user.is_authenticated()


class SuperAdminRequired(permissions.BasePermission):
    def has_permission(self, request, view):
        return self.request.user.admin_type in [SUPER_ADMIN, ADMIN]
