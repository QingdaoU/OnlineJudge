# coding=utf-8
import urllib
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from utils.shortcuts import error_response, error_page

from account.models import SUPER_ADMIN, ADMIN
from .models import (Contest, PASSWORD_PROTECTED_CONTEST, PASSWORD_PROTECTED_GROUP_CONTEST, PUBLIC_CONTEST, GROUP_CONTEST,
                     CONTEST_ENDED, CONTEST_NOT_START, CONTEST_UNDERWAY)


def check_user_contest_permission(func):
    @wraps(func)
    def _check_user_contest_permission(*args, **kwargs):
        """
        这个函数检查当前的这个比赛对于 request 的用户来说能不能参加
        需要比较：比赛的开始和结束时间、比赛是否有密码、比赛是不是限定指定小组参加
        如果是有密码或者限定指定小组参加的话，即使比赛已经结束，那么也是可以看到所有的题目和结果的
        否则不能看到这个比赛的题目结果排名等等
        """
        # CBV 的情况，第一个参数是self，第二个参数是request
        if len(args) == 2:
            request = args[-1]
        else:
            request = args[0]

        if not request.user.is_authenticated():
            if request.is_ajax():
                return error_response(u"请先登录")
            else:
                return HttpResponseRedirect("/login/?__from=" + urllib.quote(request.path))

        # kwargs 就包含了 url 里面的参数
        if "contest_id" in kwargs:
            contest_id = kwargs["contest_id"]
        elif "contest_id" in request.data:
            contest_id = request.data["contest_id"]
        elif "contest_id" in request.GET:
            contest_id = request.GET["contest_id"]
        else:
            if request.is_ajax():
                return error_response(u"参数错误")
            else:
                return error_page(request, u"参数错误")

        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            if request.is_ajax():
                return error_response(u"比赛不存在")
            else:
                return error_page(request, u"比赛不存在")

        if request.user.admin_type == SUPER_ADMIN or request.user == contest.created_by:
            return func(*args, **kwargs)
        if request.user.admin_type == ADMIN:
            contest_set = Contest.objects.filter(groups__in=request.user.managed_groups.all())
            if contest in contest_set:
                return func(*args, **kwargs)
        # 管理员可见隐藏的比赛，已经先判断了身份
        if not contest.visible:
            if request.is_ajax():
                return error_response(u"比赛不存在")
            else:
                return error_page(request, u"比赛不存在")

        # 有密码的公开赛
        if contest.contest_type == PASSWORD_PROTECTED_CONTEST:
            # 没有输入过密码
            if contest.id not in request.session.get("contests", []):
                if request.is_ajax():
                    return error_response(u"请先输入密码")
                else:
                    return render(request, "oj/contest/no_contest_permission.html",
                                  {"reason": "password_protect", "show_tab": False, "contest": contest})

        # 指定小组参加的
        if contest.contest_type == GROUP_CONTEST:
            if not contest.groups.filter(id__in=request.user.group_set.all()).exists():
                if request.is_ajax():
                    return error_response(u"只有指定小组的可以参加这场比赛")
                else:
                    return render(request, "oj/contest/no_contest_permission.html",
                                  {"reason": "group_limited", "show_tab": False, "contest": contest})
                                  
        if contest.contest_type == PASSWORD_PROTECTED_GROUP_CONTEST:
            if not contest.groups.filter(id__in=request.user.group_set.all()).exists():
                if contest.id not in request.session.get("contests", []):
                    if request.is_ajax():
                        return error_response(u"请先输入密码")
                    else:
                        return render(request, "oj/contest/no_contest_permission.html",
                                      {"reason": "password_protect", "show_tab": False, "contest": contest})

        # 比赛没有开始
        if contest.status == CONTEST_NOT_START:
            if request.is_ajax():
                return error_response(u"比赛还没有开始")
            else:
                return render(request, "oj/contest/no_contest_permission.html",
                              {"reason": "contest_not_start", "show_tab": False, "contest": contest})

        # 比赛已经结束了，只拦截 ajax 的答案提交
        if contest.status == CONTEST_ENDED and request.path == reverse("contest_submission_api") and request.is_ajax():
            return error_response(u"比赛已经结束")

        return func(*args, **kwargs)

    return _check_user_contest_permission
