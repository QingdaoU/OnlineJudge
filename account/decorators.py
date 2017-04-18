import functools

from utils.api import JSONResponse

from .models import ProblemPermission


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
                return self.error("Your account is disabled")
            return self.func(*args, **kwargs)
        else:
            return self.error("Please login in first")

    def check_permission(self):
        raise NotImplementedError()


class login_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated()


class super_admin_required(BasePermissionDecorator):
    def check_permission(self):
        user = self.request.user
        return user.is_authenticated() and user.is_super_admin()


class admin_role_required(BasePermissionDecorator):
    def check_permission(self):
        user = self.request.user
        return user.is_authenticated() and user.is_admin_role()


class problem_permission_required(admin_role_required):
    def check_permission(self):
        if not super(problem_permission_required, self).check_permission():
            return False
        if self.request.user.problem_permission == ProblemPermission.NONE:
            return False
        return True
