# coding=utf-8
import json
import datetime

from django.shortcuts import render
from django.db import IntegrityError
from django.utils import dateparse
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.utils.timezone import now

from rest_framework.views import APIView

from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, paginate, error_page)
from account.models import SUPER_ADMIN, User
from account.decorators import login_required
from group.models import Group
from .models import Contest, ContestProblem, ContestSubmission
from .models import GROUP_CONTEST, PUBLIC_CONTEST, PASSWORD_PROTECTED_CONTEST
from .decorators import check_user_contest_permission
from .serializers import (CreateContestSerializer, ContestSerializer, EditContestSerializer,
                          CreateContestProblemSerializer, ContestProblemSerializer,
                          ContestPasswordVerifySerializer,
                          EditContestProblemSerializer)
from oj.settings import REDIS_CACHE
import redis


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
            if data["contest_type"] == PASSWORD_PROTECTED_CONTEST:
                if not data["password"]:
                    return error_response(u"此比赛为有密码的公开赛，密码不可为空")

            # 没有密码的公开赛 没有密码的小组赛
            elif data["contest_type"] == GROUP_CONTEST:
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
                                                 real_time_rank=data["real_time_rank"], password=data["password"],
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
            if data["contest_type"] in [PUBLIC_CONTEST, PASSWORD_PROTECTED_CONTEST]:
                if request.user.admin_type != SUPER_ADMIN:
                    return error_response(u"只有超级管理员才可创建公开赛")
            if data["contest_type"] == PASSWORD_PROTECTED_CONTEST:
                if not data["password"]:
                    return error_response(u"此比赛为有密码的公开赛，密码不可为空")
            elif data["contest_type"] == GROUP_CONTEST:
                if request.user.admin_type == SUPER_ADMIN:
                    groups = Group.objects.filter(id__in=data["groups"])
                else:
                    groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                if not groups.count():
                    return error_response(u"请至少选择一个小组")
            if data["start_time"] >= data["end_time"]:
                return error_response(u"比赛的开始时间不能晚于或等于比赛结束的时间")
            if request.user.admin_type != SUPER_ADMIN and request.user != contest.created_by:
                return error_response(u"你无权修改该比赛!")
            contest.title = data["title"]
            contest.description = data["description"]
            contest.mode = data["mode"]
            contest.contest_type = data["contest_type"]
            contest.real_time_rank = data["real_time_rank"]
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
        if request.user.admin_type == SUPER_ADMIN:
            contest = Contest.objects.all().order_by("-create_time")
        else:
            contest = Contest.objects.filter(created_by=request.user).order_by("-create_time")
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
                                                            sort_index=data["sort_index"],
                                                            score=data["score"])
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
                return error_response(u"你无权修改该题目!")
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
            contest_problem.score = data["score"]
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
        if request.user.admin_type == SUPER_ADMIN:
            contest_problem = ContestProblem.objects.all().order_by("sort_index")
        else:
            contest_problem = ContestProblem.objects.filter(created_by=request.user).order_by("sort_index")
        visible = request.GET.get("visible", None)
        if visible:
            contest_problem = contest_problem.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            contest_problem = contest_problem.filter(Q(title__contains=keyword) |
                                                     Q(description__contains=keyword))
        contest_id = request.GET.get("contest_id", None)
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id)
            except Contest.DoesNotExist:
                return error_response(u"该比赛不存在!")
            contest_problem = contest_problem.filter(contest=contest).order_by("sort_index")

        return paginate(request, contest_problem, ContestProblemSerializer)


class ContestPasswordVerifyAPIView(APIView):
    @login_required
    def post(self, request):
        serializer = ContestPasswordVerifySerializer(data=request.data)
        if serializer.is_valid():
            data = request.data
            try:
                contest = Contest.objects.get(id=data["contest_id"], contest_type=PASSWORD_PROTECTED_CONTEST)
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
        contest_problem = ContestProblem.objects.get(id=contest_problem_id, visible=True)
    except ContestProblem.DoesNotExist:
        return error_page(request, u"比赛题目不存在")
    warning = u"您已经提交过本题的正确答案，重复提交可能造成时间累计。"
    show_warning = False
    try:
        submission = ContestSubmission.objects.get(user=request.user, contest=contest, problem=contest_problem)
        show_warning = submission.ac
    except ContestSubmission.DoesNotExist:
        pass

    # 已经结束
    if contest.status == -1:
        show_warning = True
        warning = u"比赛已经结束"
    return render(request, "oj/contest/contest_problem.html", {"contest_problem": contest_problem, "contest": contest,
                                                               "samples": json.loads(contest_problem.samples),
                                                               "show_warning": show_warning, "warning": warning})


@check_user_contest_permission
def contest_problems_list_page(request, contest_id):
    """
    比赛所有题目的列表页
    """
    try:
        contest = Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return error_page(request, u"比赛不存在")
    contest_problems = ContestProblem.objects.filter(contest=contest).order_by("sort_index")
    submissions = ContestSubmission.objects.filter(user=request.user, contest=contest)
    state = {}
    for item in submissions:
        state[item.problem_id] = item.ac
    for item in contest_problems:
        if item.id in state:
            if state[item.id]:
                item.state = 1
            else:
                item.state = 2
        else:
            item.state = 0
    return render(request, "oj/contest/contest_problems_list.html", {"contest_problems": contest_problems,
                                                                     "contest": {"id": contest_id}})


def contest_list_page(request, page=1):
    """
    所有比赛的列表页
    """
    # 正常情况
    contests = Contest.objects.filter(visible=True).order_by("-create_time")

    # 搜索的情况
    keyword = request.GET.get("keyword", None)
    if keyword:
        contests = contests.filter(Q(title__contains=keyword) | Q(description__contains=keyword))

    # 筛选我能参加的比赛
    join = request.GET.get("join", None)
    if request.user.is_authenticated and join:
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


def _cmp(x, y):
    if x["total_ac"] > y["total_ac"]:
        return 1
    elif x["total_ac"] < y["total_ac"]:
        return -1
    else:
        if x["total_time"] < y["total_time"]:
            return 1
        else:
            return -1


def get_the_formatted_time(seconds):
    if not seconds:
        return ""
    result = str(seconds % 60)
    if seconds % 60 < 10:
        result = "0" + result
    result = str((seconds % 3600) / 60) + ":" + result
    if (seconds % 3600) / 60 < 10:
        result = "0" + result
    result = str(seconds / 3600) + ":" + result
    if seconds / 3600 < 10:
        result = "0" + result
    return result


@check_user_contest_permission
def contest_rank_page(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    contest_problems = ContestProblem.objects.filter(contest=contest).order_by("sort_index")
    r = redis.Redis(host=REDIS_CACHE["host"], port=REDIS_CACHE["port"], db=REDIS_CACHE["db"])
    if contest.real_time_rank:
        # 更新rank
        result = ContestSubmission.objects.filter(contest=contest).values("user_id"). \
            annotate(total_submit=Sum("total_submission_number"))
        for i in range(0, len(result)):
            # 这个人所有的提交
            submissions = ContestSubmission.objects.filter(user_id=result[i]["user_id"], contest_id=contest_id)
            result[i]["submissions"] = {}
            result[i]["problems"] = []
            for problem in contest_problems:
                try:
                    status = submissions.get(problem=problem)
                    result[i]["problems"].append({
                        "first_achieved": status.first_achieved,
                        "ac": status.ac,
                        "failed_number": status.total_submission_number,
                        "ac_time": get_the_formatted_time(status.ac_time)})
                    if status.ac:
                        result[i]["problems"][-1]["failed_number"] -= 1
                except ContestSubmission.DoesNotExist:
                    result[i]["problems"].append({})
            result[i]["total_ac"] = submissions.filter(ac=True).count()
            user= User.objects.get(id=result[i]["user_id"])
            result[i]["username"] = user.username
            result[i]["real_name"] = user.real_name
            result[i]["total_time"] = get_the_formatted_time(submissions.filter(ac=True).aggregate(total_time=Sum("total_time"))["total_time"])

        result = sorted(result, cmp=_cmp, reverse=True)
        r.set("contest_rank_" + contest_id, json.dumps(list(result)))
    else:
        # 从缓存读取排名信息
        result = r.get("contest_rank_" + contest_id)
        if result:
            result = json.loads(result)
        else:
            result = []

    return render(request, "oj/contest/contest_rank.html",
                  {"contest": contest, "contest_problems": contest_problems,
                   "result": result,
                   "auto_refresh": request.GET.get("auto_refresh", None) == "true",
                   "show_real_name": request.GET.get("show_real_name", None) == "true",
                   "real_time_rank": contest.real_time_rank})


class ContestTimeAPIView(APIView):
    """
    获取比赛开始或者结束的倒计时，返回毫秒数字
    """
    def get(self, request):
        t = request.GET.get("type", "start")
        contest_id = request.GET.get("contest_id", -1)
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return error_response(u"比赛不存在")
        if t == "start":
            # 距离开始还有多长时间
            return success_response(int((contest.start_time - now()).total_seconds() * 1000))
        else:
            # 距离结束还有多长时间
            return success_response(int((contest.end_time - now()).total_seconds() * 1000))
