import functools

from django.utils.translation import ugettext as _

from utils.api import JSONResponse

from .models import AdminType


class BasePermissionDecorator(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        return functools.partial(self.__call__, obj)

    def error(self, data):
        return JSONResponse.response({"error": "permission-denied", "data": data})

    def __call__(self, *args, **kwargs):
        self.request = args[1]

        if self.check_permission():
            if self.request.user.is_disabled:
                return self.error(_("Your account is disabled"))
            return self.func(*args, **kwargs)
        else:
            return self.error(_("Please login in first"))

    def check_permission(self):
        raise NotImplementedError()


class login_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated()


class super_admin_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated() and \
               self.request.user.admin_type == AdminType.SUPER_ADMIN


class admin_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated() and \
               self.request.user.admin_type in [AdminType.SUPER_ADMIN, AdminType.ADMIN]
