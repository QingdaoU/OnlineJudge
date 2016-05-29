# coding=utf-8
import json
import os
import datetime
import hashlib

from django.shortcuts import render
from django.db import IntegrityError
from django.utils import dateparse
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.conf import settings

from rest_framework.views import APIView

from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, paginate, error_page, paginate_data)
from account.models import SUPER_ADMIN, User
from account.decorators import login_required, super_admin_required
from group.models import Group, AdminGroupRelation, UserGroupRelation
from utils.cache import get_cache_redis
from submission.models import Submission
from problem.models import Problem
from .models import (Contest, ContestProblem, CONTEST_ENDED,
                     CONTEST_NOT_START, CONTEST_UNDERWAY, ContestRank)
from .models import GROUP_CONTEST, PUBLIC_CONTEST, PASSWORD_PROTECTED_CONTEST, PASSWORD_PROTECTED_GROUP_CONTEST
from .decorators import check_user_contest_permission
from .serializers import (CreateContestSerializer, ContestSerializer, EditContestSerializer,
                          CreateContestProblemSerializer, ContestProblemSerializer,
                          ContestPasswordVerifySerializer,
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
            # 首先判断比赛的类型： 0 即为是小组赛(GROUP_CONTEST)，1 即为是无密码的公开赛(PUBLIC_CONTEST)，
            # 2 即为是有密码的公开赛(PASSWORD_PUBLIC_CONTEST)
            # 此时为有密码的公开赛，并且此时只能超级管理员才有权限此创建比赛
            if data["contest_type"] in [PUBLIC_CONTEST, PASSWORD_PROTECTED_CONTEST]:
                if request.user.admin_type != SUPER_ADMIN:
                    return error_response(u"只有超级管理员才可创建公开赛")

            if data["contest_type"] in [PASSWORD_PROTECTED_CONTEST, PASSWORD_PROTECTED_GROUP_CONTEST]:
                if not data["password"]:
                    return error_response(u"此比赛为有密码的比赛，密码不可为空")
            # 没有密码的公开赛 没有密码的小组赛
            if data["contest_type"] == GROUP_CONTEST or data["contest_type"] == PASSWORD_PROTECTED_GROUP_CONTEST:
                if request.user.admin_type == SUPER_ADMIN:
                    groups = Group.objects.filter(id__in=data["groups"])
                else:
                    groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                if not groups.count():
                    return error_response(u"请至少选择一个小组")
            if data["start_time"] >= data["end_time"]:
                return error_response(u"比赛的开始时间必须早于比赛结束的时间")
            try:
                contest = Contest.objects.create(title=data["title"], description=data["description"],
                                                 contest_type=data["contest_type"],
                                                 real_time_rank=data["real_time_rank"], password=data["password"],
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
                # 超级管理员可以编辑所有的
                contest = Contest.objects.get(id=data["id"])
                if request.user.admin_type != SUPER_ADMIN:
                    contest_set = Contest.objects.filter(groups__in=request.user.managed_groups.all())
                    if contest not in contest_set:
                        return error_response(u"无权访问！")
            except Contest.DoesNotExist:
                return error_response(u"该比赛不存在！")
            try:
                contest = Contest.objects.get(title=data["title"])
                if contest.id != data["id"]:
                    return error_response(u"该比赛名称已经存在")
            except Contest.DoesNotExist:
                pass
            if data["contest_type"] in [PUBLIC_CONTEST, PASSWORD_PROTECTED_CONTEST]:
                if request.user.admin_type != SUPER_ADMIN:
                    return error_response(u"只有超级管理员才可创建公开赛")
            if data["contest_type"] == PASSWORD_PROTECTED_CONTEST:
                if not data["password"]:
                    return error_response(u"此比赛为有密码的公开赛，密码不可为空")
            elif data["contest_type"] in [GROUP_CONTEST, PASSWORD_PROTECTED_GROUP_CONTEST]:
                if request.user.admin_type == SUPER_ADMIN:
                    groups = Group.objects.filter(id__in=data["groups"])
                else:
                    groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                if not groups.count():
                    return error_response(u"请至少选择一个小组")
            if data["start_time"] >= data["end_time"]:
                return error_response(u"比赛的开始时间必须早于比赛结束的时间")

            # 之前是封榜，现在要开放，需要清除缓存
            if contest.real_time_rank == False and data["real_time_rank"] == True:
                r = get_cache_redis()
                cache_key = str(contest.id) + "_rank_cache"
                r.delete(cache_key)

            contest.title = data["title"]
            contest.description = data["description"]
            contest.contest_type = data["contest_type"]
            contest.real_time_rank = data["real_time_rank"]
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
        contest_id = request.GET.get("contest_id", None)
        if contest_id:
            try:
                # 普通管理员只能获取自己创建的题目
                # 超级管理员可以获取全部的题目
                contest = Contest.objects.get(id=contest_id)
                if request.user.admin_type != SUPER_ADMIN:
                    contest_set = Contest.objects.filter(groups__in=request.user.managed_groups.all())
                    if contest not in contest_set:
                        return error_response(u"比赛不存在")
                return success_response(ContestSerializer(contest).data)
            except Contest.DoesNotExist:
                return error_response(u"比赛不存在")

        if request.user.admin_type == SUPER_ADMIN:
            contest = Contest.objects.all().order_by("-create_time")
        else:
            contest = Contest.objects.filter(groups__in=request.user.managed_groups.all()).distinct().order_by("-create_time")
        visible = request.GET.get("visible", None)
        if visible:
            contest = contest.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            contest = contest.filter(Q(title__contains=keyword) |
                                     Q(description__contains=keyword))
        return paginate(request, contest, ContestSerializer)


class ContestProblemAdminAPIView(APIView):
    def _spj_version(self, code):
        if code is None:
            return None
        return hashlib.md5(code.encode("utf-8")).hexdigest()

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
                if request.user.admin_type != SUPER_ADMIN:
                    contest_set = Contest.objects.filter(groups__in=request.user.managed_groups.all())
                    if contest not in contest_set:
                        return error_response(u"比赛不存在")
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
                                                            spj=data["spj"],
                                                            spj_language=data["spj_language"],
                                                            spj_code=data["spj_code"],
                                                            spj_version=self._spj_version(data["spj_code"]),
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

            contest = Contest.objects.get(id=contest_problem.contest_id)
            if request.user.admin_type != SUPER_ADMIN and contest.created_by != request.user:
                return error_response(u"比赛不存在")
            contest_problem.title = data["title"]
            contest_problem.description = data["description"]
            contest_problem.input_description = data["input_description"]
            contest_problem.output_description = data["output_description"]
            contest_problem.test_case_id = data["test_case_id"]
            contest_problem.time_limit = data["time_limit"]
            contest_problem.memory_limit = data["memory_limit"]
            contest_problem.spj = data["spj"]
            contest_problem.spj_language = data["spj_language"]
            contest_problem.spj_code = data["spj_code"]
            contest_problem.spj_version = self._spj_version(data["spj_code"])
            contest_problem.samples = json.dumps(data["samples"])
            contest_problem.hint = data["hint"]
            contest_problem.visible = data["visible"]
            contest_problem.sort_index = data["sort_index"]
            contest_problem.last_update_time = now()
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
                if request.user.admin_type != SUPER_ADMIN and contest_problem.created_by != request.user:
                    return error_response(u"比赛题目不存在")
                return success_response(ContestProblemSerializer(contest_problem).data)
            except ContestProblem.DoesNotExist:
                return error_response(u"比赛题目不存在")

        contest_problems = ContestProblem.objects.all().order_by("sort_index")
        if request.user.admin_type != SUPER_ADMIN:
            contest_problems = contest_problems.filter(created_by=request.user).order_by("sort_index")
        visible = request.GET.get("visible", None)
        if visible:
            contest_problems = contest_problems.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            contest_problems = contest_problems.filter(Q(title__contains=keyword) |
                                                       Q(description__contains=keyword))
        contest_id = request.GET.get("contest_id", None)
        if contest_id:
            contest_problems = contest_problems.filter(contest__id=contest_id).order_by("sort_index")

        return paginate(request, contest_problems, ContestProblemSerializer)


class MakeContestProblemPublicAPIView(APIView):
    @super_admin_required
    def post(self, request):
        problem_id = request.data.get("problem_id", -1)
        try:
            problem = ContestProblem.objects.get(id=problem_id, is_public=False)
            if problem.contest.status != CONTEST_ENDED:
                return error_response(u"比赛还没有结束，不能公开题目")
            problem.is_public = True
            problem.save()
        except ContestProblem.DoesNotExist:
            return error_response(u"比赛不存在")
        Problem.objects.create(title=problem.title, description=problem.description,
                               input_description=problem.input_description,
                               output_description=problem.output_description,
                               samples=problem.samples,
                               test_case_id=problem.test_case_id,
                               hint=problem.hint, created_by=problem.created_by,
                               time_limit=problem.time_limit, memory_limit=problem.memory_limit,
                               visible=False, difficulty=-1, source=problem.contest.title)
        problem.is_public = True
        problem.save()
        return success_response(u"创建成功")


class ContestPasswordVerifyAPIView(APIView):
    @login_required
    def post(self, request):
        serializer = ContestPasswordVerifySerializer(data=request.data)
        if serializer.is_valid():
            data = request.data
            try:
                contest = Contest.objects.get(id=data["contest_id"], contest_type__in=[PASSWORD_PROTECTED_CONTEST,PASSWORD_PROTECTED_GROUP_CONTEST])
            except Contest.DoesNotExist:
                return error_response(u"比赛不存在")

            if data["password"] != contest.password:
                return error_response(u"密码错误")
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
    """
    单个比赛的详情页
    """
    contest = Contest.objects.get(id=contest_id)
    return render(request, "oj/contest/contest_index.html", {"contest": contest})


@check_user_contest_permission
def contest_problem_page(request, contest_id, contest_problem_id):
    """
    单个比赛题目的详情页
    """
    contest = Contest.objects.get(id=contest_id)
    try:
        problem = ContestProblem.objects.get(id=contest_problem_id, visible=True)
    except ContestProblem.DoesNotExist:
        return error_page(request, u"比赛题目不存在")
    warning = u"您已经提交过本题的正确答案，重复提交可能造成时间累计。"
    show_warning = False

    try:
        rank = ContestRank.objects.get(user=request.user, contest=contest)
        # 提示已经 ac 过这道题了
        show_warning = rank.submission_info.get(str(problem.id), {"is_ac": False})["is_ac"]
    except ContestRank.DoesNotExist:
        pass

    # 已经结束
    if contest.status == CONTEST_ENDED:
        show_warning = True
        warning = u"比赛已经结束"
    elif contest.status == CONTEST_NOT_START:
        show_warning = True
        warning = u"比赛没有开始，您是管理员，可以提交和测试题目，但是目前的提交不会计入排名。"

    show_submit_code_area = False
    if contest.status == CONTEST_UNDERWAY or \
                    request.user.admin_type == SUPER_ADMIN or \
                    request.user == contest.created_by:
        show_submit_code_area = True
    else:
        contest_set = Contest.objects.filter(groups__in=request.user.managed_groups.all())
        if contest in contest_set:
            show_submit_code_area = True
    return render(request, "oj/problem/contest_problem.html", {"problem": problem,
                                                               "contest": contest,
                                                               "samples": json.loads(problem.samples),
                                                               "show_warning": show_warning,
                                                               "warning": warning,
                                                               "show_submit_code_area": show_submit_code_area})


@check_user_contest_permission
def contest_problems_list_page(request, contest_id):
    """
    比赛所有题目的列表页
    """
    contest = Contest.objects.get(id=contest_id)
    contest_problems = ContestProblem.objects.filter(contest=contest, visible=True).select_related("contest").order_by("sort_index")
    return render(request, "oj/contest/contest_problems_list.html", {"contest_problems": contest_problems,
                                                                     "contest": {"id": contest_id}})


def contest_list_page(request, page=1):
    """
    所有比赛的列表页
    """
    # 正常情况
    contests = Contest.objects.filter(visible=True).order_by("-create_time")

    # 搜索的情况
    keyword = request.GET.get("keyword", "").strip()
    if keyword:
        contests = contests.filter(Q(title__contains=keyword) | Q(description__contains=keyword))

    # 筛选我能参加的比赛
    join = request.GET.get("join", None)
    if request.user.is_authenticated() and join:
        contests = contests.filter(Q(contest_type__in=[1, 2]) | Q(groups__in=request.user.group_set.all())). \
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

    return render(request, "oj/contest/contest_list.html",
                  {"contests": current_page, "page": int(page),
                   "previous_page": previous_page, "next_page": next_page,
                   "keyword": keyword, "join": join})


def _get_rank(contest_id):
    rank = ContestRank.objects.filter(contest_id=contest_id). \
            select_related("user"). \
            order_by("-total_ac_number", "total_time"). \
            values("id", "user__id", "user__username", "user__real_name", "user__userprofile__student_id",
                   "contest_id", "submission_info", "total_submission_number", "total_ac_number", "total_time")
    rank_number = 1
    for item in rank:
        # 只有有ac的题目而且不是打星的队伍才参与排名
        if item["total_ac_number"] > 0 and item["user__username"][0] != "*":
            item["rank_number"] = rank_number
            rank_number += 1
    return rank


@check_user_contest_permission
def contest_rank_page(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    contest_problems = ContestProblem.objects.filter(contest=contest, visible=True).order_by("sort_index")

    force_real_time_rank = False
    if request.GET.get("force_real_time_rank") == "true" and (request.user.admin_type == SUPER_ADMIN or request.user == contest.created_by):
        rank = _get_rank(contest_id)
        force_real_time_rank = True
    else:
        r = get_cache_redis()
        cache_key = str(contest_id) + "_rank_cache"
        rank = r.get(cache_key)

        if not rank:
            rank = _get_rank(contest_id)
            r.set(cache_key, json.dumps([dict(item) for item in rank]))
        else:
            rank = json.loads(rank)

            # 2016-05-19 增加了缓存项目,以前的缓存主动失效
            if rank and "rank_number" not in rank[0]:
                rank = _get_rank(contest_id)
                r.set(cache_key, json.dumps([dict(item) for item in rank]))

    return render(request, "oj/contest/contest_rank.html",
                  {"rank": rank, "contest": contest,
                   "contest_problems": contest_problems,
                   "auto_refresh": request.GET.get("auto_refresh", None) == "true",
                   "show_real_name": request.GET.get("show_real_name", None) == "true",
                   "force_real_time_rank": force_real_time_rank})


class ContestTimeAPIView(APIView):
    """
    获取比赛开始或者结束的倒计时，返回毫秒数字
    """

    def get(self, request):
        contest_id = request.GET.get("contest_id", -1)
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return error_response(u"比赛不存在")
        return success_response({"start": int((contest.start_time - now()).total_seconds() * 1000),
                                 "end": int((contest.end_time - now()).total_seconds() * 1000),
                                 "status": contest.status})


@login_required
def contest_problem_my_submissions_list_page(request, contest_id, contest_problem_id):
    """
    我比赛单个题目的所有提交列表
    """
    try:
        Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return error_page(request, u"比赛不存在")
    try:
        contest_problem = ContestProblem.objects.get(id=contest_problem_id, visible=True)
    except ContestProblem.DoesNotExist:
        return error_page(request, u"比赛问题不存在")
    submissions = Submission.objects.filter(user_id=request.user.id, problem_id=contest_problem.id, contest_id=contest_id). \
        order_by("-create_time"). \
        values("id", "result", "create_time", "accepted_answer_time", "language")
    return render(request, "oj/submission/problem_my_submissions_list.html",
                  {"submissions": submissions, "problem": contest_problem})


@check_user_contest_permission
def contest_problem_submissions_list_page(request, contest_id, page=1):
    """
    单个比赛中的所有提交（包含自己和别人，自己可查提交结果，其他人不可查）
    """
    try:
        contest = Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return error_page(request, u"比赛不存在")

    submissions = Submission.objects.filter(contest_id=contest_id). \
        values("id", "contest_id", "problem_id", "result", "create_time",
               "accepted_answer_time", "language", "user_id").order_by("-create_time")

    # 如果比赛已经开始，就不再显示之前测试题目的提交
    if contest.status != CONTEST_NOT_START:
        submissions = submissions.filter(create_time__gte=contest.start_time)

    user_id = request.GET.get("user_id", None)
    if user_id:
        submissions = submissions.filter(user_id=request.GET.get("user_id"))

    problem_id = request.GET.get("problem_id", None)
    if problem_id:
        submissions = submissions.filter(problem_id=problem_id)

    # 封榜的时候只能看到自己的提交
    if not contest.real_time_rank:
        if not (request.user.admin_type == SUPER_ADMIN or request.user == contest.created_by):
            submissions = submissions.filter(user_id=request.user.id)

    language = request.GET.get("language", None)
    filter = None
    if language:
        submissions = submissions.filter(language=int(language))
        filter = {"name": "language", "content": language}
    result = request.GET.get("result", None)
    if result:
        submissions = submissions.filter(result=int(result))
        filter = {"name": "result", "content": result}

    paginator = Paginator(submissions, 20)
    try:
        submissions = paginator.page(int(page))
    except Exception:
        return error_page(request, u"不存在的页码")

    # 为查询题目标题创建新字典
    title = {}
    contest_problems = ContestProblem.objects.filter(contest=contest)
    for item in contest_problems:
        title[item.id] = item.title
    for item in submissions:
        item['title'] = title[item['problem_id']]

    previous_page = next_page = None
    try:
        previous_page = submissions.previous_page_number()
    except Exception:
        pass
    try:
        next_page = submissions.next_page_number()
    except Exception:
        pass

    for item in submissions:
        # 自己提交的 管理员和创建比赛的可以看到所有的提交链接
        if item["user_id"] == request.user.id or request.user.admin_type == SUPER_ADMIN or \
                        request.user == contest.created_by:
            item["show_link"] = True
        else:
            item["show_link"] = False

    return render(request, "oj/contest/submissions_list.html",
                  {"submissions": submissions, "page": int(page),
                   "previous_page": previous_page, "next_page": next_page, "start_id": int(page) * 20 - 20,
                   "contest": contest, "filter": filter, "user_id": user_id, "problem_id": problem_id})
