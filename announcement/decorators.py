# coding=utf-8
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from utils.shortcuts import error_response, error_page

from account.models import SUPER_ADMIN
from .models import Announcement


def check_user_announcement_permission(func):
    @wraps(func)
    def _check_user_announcement_permission(*args, **kwargs):
        """
        这个函数检测当前用户能否查看这个公告
        """
        # CBV 的情况，第一个参数是self，第二个参数是request
        if len(args) == 2:
            request = args[-1]
        else:
            request = args[0]

        if "announcement_id" not in kwargs:
            return error_page(request, u"参数错误")
        announcement_id = kwargs["announcement_id"]

        try:
            announcement = Announcement.objects.get(id=announcement_id, visible=True)
        except Announcement.DoesNotExist:
            return error_page(request, u"公告不存在")

        # 如果公告是只有部分小组可见的
        if not announcement.is_global:
            # 用户必须是登录状态的
            if not request.user.is_authenticated():
                return HttpResponseRedirect("/login/")
            if not announcement.groups.filter(id__in=request.user.group_set.all()).exists():
                return error_page(request, u"公告不存在")
        return func(*args, **kwargs)

    return _check_user_announcement_permission
