# coding=utf-8
from functools import wraps

from account.models import SUPER_ADMIN
from utils.shortcuts import error_response
from .models import Problem


def check_user_problem_permission(func):
    @wraps(func)
    def check(*args, **kwargs):
        # 在class based views 里面，args 有两个元素，一个是self, 第二个才是request，
        # 在function based views 里面，args 只有request 一个参数
        if len(args) == 2:
            request = args[-1]
        else:
            request = args[0]

        # 这是在后台使用的url middleware 已经确保用户是登录状态的了
        try:
            problem = Problem.objects.get(id=request.data.get("id", -1))
        except Problem.DoesNotExist:
            return error_response(u"问题不存在")

        if request.user.admin_type == SUPER_ADMIN:
            return func(*args, **kwargs)
        else:
            if problem.created_by != request.user:
                return error_response(u"问题不存在")
            return func(*args, **kwargs)

    return check
