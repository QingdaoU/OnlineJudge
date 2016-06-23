# coding=utf-8
from __future__ import unicode_literals
import urllib
import functools

from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from utils.shortcuts import error_response, error_page
from .models import AdminType


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
            if self.request.user.is_disabled:
                if self.request.is_ajax():
                    return error_response(_("Your account is disabled"))
                else:
                    return error_page(self.request, _("Your account is disabled"))
            return self.func(*args, **kwargs)
        else:
            if self.request.is_ajax():
                return error_response(_("Please login in first"))
            else:
                return HttpResponseRedirect("/login/?__from=" + urllib.quote(self.request.path))

    def check_permission(self):
        raise NotImplementedError()


class login_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated()


class super_admin_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated() and self.request.user.admin_type == AdminType.SUPER_ADMIN


class admin_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated() and self.request.user.admin_type in [AdminType.SUPER_ADMIN, AdminType.ADMIN]
