# coding=utf-8
import json
import datetime
from functools import wraps
from django.utils.timezone import now
from django.shortcuts import render
from django.db import IntegrityError
from django.utils import dateparse
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.views import APIView
from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, paginate, rand_str, error_page)

from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN
from account.decorators import login_required
from group.models import Group
from announcement.models import Announcement

from .models import Contest, ContestProblem
from .decorators import check_user_contest_permission
from .serializers import (CreateContestSerializer, ContestSerializer, EditContestSerializer,
                          CreateContestProblemSerializer, ContestProblemSerializer,
                          EditContestProblemSerializer, ContestPasswordVerifySerializer,
                          EditContestProblemSerializer)


class ContestAdminAPIView(APIView):
    def post(self, request):
        """
        比赛发布json api接口
        ---
        request_serializer: CreateContestSerializer
        response_serializer: ContestSerializer
        """
        serializer = CreateContestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            groups = []
            # 首先判断比赛的类型： 0 即为是小组赛，1 即为是无密码的公开赛，2 即为是有密码的公开赛
            # 此时为有密码的公开赛，并且此时只能超级管理员才有权限此创建比赛
            if data["contest_type"] in [1, 2]:
                if request.user.admin_type != SUPER_ADMIN:
                    return error_response(u"只有超级管理员才可创建公开赛")
            if data["contest_type"] == 2:
                if not data["password"]:
                    return error_response(u"此比赛为有密码的公开赛，密码不可为空")

            # 没有密码的公开赛 没有密码的小组赛
            elif data["contest_type"] == 0:
                if request.user.admin_type == SUPER_ADMIN:
                    groups = Group.objects.filter(id__in=data["groups"])
                else:
                    groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                if not groups.count():
                    return error_response(u"请至少选择一个小组")
            if data["start_time"] >= data["end_time"]:
                return error_response(u"比赛的开始时间不能晚于或等于比赛结束的时间")
            try:
                contest = Contest.objects.create(title=data["title"], description=data["description"],
                                                 mode=data["mode"], contest_type=data["contest_type"],
                                                 show_rank=data["show_rank"], password=data["password"],
                                                 show_user_submission=data["show_user_submission"],
                                                 start_time=dateparse.parse_datetime(data["start_time"]),
                                                 end_time=dateparse.parse_datetime(data["end_time"]),
                                                 created_by=request.user, visible=data["visible"])
            except IntegrityError:
                return error_response(u"比赛名已经存在")
            contest.groups.add(*groups)
            return success_response(ContestSerializer(contest).data)
        else:
            return serializer_invalid_response(serializer)

    def put(self, request):
        """
        比赛编辑json api接口
        ---
        request_serializer: EditContestSerializer
        response_serializer: ContestSerializer
        """
        serializer = EditContestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            groups = []
            try:
                contest = Contest.objects.get(id=data["id"])
            except Contest.DoesNotExist:
                return error_response(u"该比赛不存在！")
            try:
                contest = Contest.objects.get(title=data["title"])
                if contest.id != data["id"]:
                    return error_response(u"该比赛名称已经存在")
            except Contest.DoesNotExist:
                pass
            if data["contest_type"] in [1, 2]:
                if request.user.admin_type != SUPER_ADMIN:
                    return error_response(u"只有超级管理员才可创建公开赛")
            if data["contest_type"] == 2:
                if not data["password"]:
                    return error_response(u"此比赛为有密码的公开赛，密码不可为空")
            elif data["contest_type"] == 0:
                if request.user.admin_type == SUPER_ADMIN:
                    groups = Group.objects.filter(id__in=data["groups"])
                else:
                    groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                if not groups.count():
                    return error_response(u"请至少选择一个小组")
            if data["start_time"] >= data["end_time"]:
                return error_response(u"比赛的开始时间不能晚于或等于比赛结束的时间")
            contest.title = data["title"]
            contest.description = data["description"]
            contest.mode = data["mode"]
            contest.contest_type = data["contest_type"]
            contest.show_rank = data["show_rank"]
            contest.show_user_submission = data["show_user_submission"]
            contest.start_time = dateparse.parse_datetime(data["start_time"])
            contest.end_time = dateparse.parse_datetime(data["end_time"])
            contest.visible = data["visible"]
            contest.password = data["password"]
            contest.save()

            contest.groups.clear()
            contest.groups.add(*groups)
            return success_response(ContestSerializer(contest).data)
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        比赛分页json api接口
        ---
        response_serializer: ContestSerializer
        """
        contest = Contest.objects.all().order_by("-last_updated_time")
        visible = request.GET.get("visible", None)
        if visible:
            contest = contest.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            contest = contest.filter(Q(title__contains=keyword) |
                                     Q(description__contains=keyword))
        return paginate(request, contest, ContestSerializer)


class ContestProblemAdminAPIView(APIView):
    def post(self, request):
        """
        比赛题目发布json api接口
        ---
        request_serializer: CreateContestProblemSerializer
        response_serializer: ContestProblemSerializer
        """
        serializer = CreateContestProblemSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                contest = Contest.objects.get(id=data["contest_id"])
            except Contest.DoesNotExist:
                return error_response(u"比赛不存在")
            contest_problem = ContestProblem.objects.create(title=data["title"],
                                                            description=data["description"],
                                                            input_description=data["input_description"],
                                                            output_description=data["output_description"],
                                                            test_case_id=data["test_case_id"],
                                                            samples=json.dumps(data["samples"]),
                                                            time_limit=data["time_limit"],
                                                            memory_limit=data["memory_limit"],
                                                            created_by=request.user,
                                                            hint=data["hint"],
                                                            contest=contest,
                                                            sort_index=data["sort_index"])
            return success_response(ContestProblemSerializer(contest_problem).data)
        else:
            return serializer_invalid_response(serializer)

    def put(self, request):
        """
        比赛题目编辑json api接口
        ---
        request_serializer: EditContestProblemSerializer
        response_serializer: ContestProblemSerializer
        """
        serializer = EditContestProblemSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                contest_problem = ContestProblem.objects.get(id=data["id"])
            except ContestProblem.DoesNotExist:
                return error_response(u"该比赛题目不存在！")
            contest_problem.title = data["title"]
            contest_problem.description = data["description"]
            contest_problem.input_description = data["input_description"]
            contest_problem.output_description = data["output_description"]
            contest_problem.test_case_id = data["test_case_id"]
            contest_problem.time_limit = data["time_limit"]
            contest_problem.memory_limit = data["memory_limit"]
            contest_problem.samples = json.dumps(data["samples"])
            contest_problem.hint = data["hint"]
            contest_problem.visible = data["visible"]
            contest_problem.sort_index = data["sort_index"]
            contest_problem.save()
            return success_response(ContestProblemSerializer(contest_problem).data)
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        比赛题目分页json api接口
        ---
        response_serializer: ContestProblemSerializer
        """
        contest_problem_id = request.GET.get("contest_problem_id", None)
        if contest_problem_id:
            try:
                contest_problem = ContestProblem.objects.get(id=contest_problem_id)
                return success_response(ContestProblemSerializer(contest_problem).data)
            except ContestProblem.DoesNotExist:
                return error_response(u"比赛题目不存在")
        contest_problem = ContestProblem.objects.all().order_by("sort_index")
        visible = request.GET.get("visible", None)
        if visible:
            contest_problem = contest_problem.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            contest_problem = contest_problem.filter(Q(title__contains=keyword) |
                                                     Q(description__contains=keyword))

        return paginate(request, contest_problem, ContestProblemSerializer)


class ContestPasswordVerifyAPIView(APIView):
    @login_required
    def post(self, request):
        serializer = ContestPasswordVerifySerializer(data=request.data)
        if serializer.is_valid():
            data = request.data
            try:
                contest = Contest.objects.get(id=data["contest_id"], contest_type=2)
            except Contest.DoesNotExist:
                return error_response(u"密码错误")

            if data["password"] != contest.password:
                return error_response(u" 密码错误")
            else:
                if "contests" not in request.session:
                    request.session["contests"] = []
                request.session["contests"].append(int(data["contest_id"]))
                # https://docs.djangoproject.com/en/dev/topics/http/sessions/#when-sessions-are-saved
                request.session.modified = True

                return success_response(True)
        else:
            return serializer_invalid_response(serializer)


@check_user_contest_permission
def contest_page(request, contest_id):
    try:
        contest = Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return error_page(request, u"比赛不存在")

    return render(request, "oj/contest/contest_index.html", {"contest": contest})


def contest_problem_page(request, contest_id, contest_problem_id):
    try:
        Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return error_page(request, u"比赛不存在")
    try:
        contest_problem = ContestProblem.objects.get(id=contest_problem_id, visible=True)
    except ContestProblem.DoesNotExist:
        return error_page(request, u"比赛题目不存在")
    return render(request, "oj/contest/contest_problem.html", {"contest_problem": contest_problem,
                                                               "samples": json.loads(contest_problem.samples)})


@check_user_contest_permission
def contest_problems_list_page(request, contest_id):
    try:
        contest_problems = ContestProblem.objects.filter(contest=Contest.objects.get(id=contest_id)).order_by("sort_index")
    except Contest.DoesNotExist:
        return error_page(request, u"比赛题目不存在")
    # 右侧的公告列表
    announcements = Announcement.objects.filter(is_global=True, visible=True).order_by("-create_time")
    return render(request, "oj/contest/contest_problems_list.html", {"contest_problems": contest_problems,
                                                                     "announcements": announcements,
                                                                     "contest": {"id": contest_id}})


def contest_list_page(request, page=1):
    # 正常情况
    contests = Contest.objects.filter(visible=True)

    # 搜索的情况
    keyword = request.GET.get("keyword", None)
    if keyword:
        contests = contests.filter(title__contains=keyword)

    # 筛选我能参加的比赛
    join = request.GET.get("join", None)
    if join:
        contests = Contest.objects.filter(Q(contest_type__in=[1, 2]) | Q(groups__in=request.user.group_set.all())).\
            filter(end_time__gt=datetime.datetime.now(), start_time__lt=datetime.datetime.now())

    paginator = Paginator(contests, 20)
    try:
        current_page = paginator.page(int(page))
    except Exception:
        return error_page(request, u"不存在的页码")

    previous_page = next_page = None

    try:
        previous_page = current_page.previous_page_number()
    except Exception:
        pass

    try:
        next_page = current_page.next_page_number()
    except Exception:
        pass

    # 右侧的公告列表
    announcements = Announcement.objects.filter(is_global=True, visible=True).order_by("-create_time")

    return render(request, "oj/contest/contest_list.html",
                  {"contests": current_page, "page": int(page),
                   "previous_page": previous_page, "next_page": next_page,
                   "keyword": keyword, "announcements": announcements,
                   "join": join})




