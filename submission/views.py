# coding=utf-8
import json

import redis
from django.shortcuts import render
from django.core.paginator import Paginator

from rest_framework.views import APIView

from judge.judger_controller.tasks import judge
from judge.judger_controller.settings import redis_config
from account.decorators import login_required
from account.models import SUPER_ADMIN


from problem.models import Problem
from contest.models import ContestProblem

from utils.shortcuts import serializer_invalid_response, error_response, success_response, error_page, paginate
from .models import Submission
from .serializers import CreateSubmissionSerializer, SubmissionSerializer
from announcement.models import Announcement

class SubmissionAPIView(APIView):
    @login_required
    def post(self, request):
        """
        提交代码
        ---
        request_serializer: CreateSubmissionSerializer
        """
        serializer = CreateSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                problem = Problem.objects.get(id=data["problem_id"])
                # 更新问题的总提交计数
                problem.total_submit_number += 1
                problem.save()
            except Problem.DoesNotExist:
                return error_response(u"题目不存在")
            submission = Submission.objects.create(user_id=request.user.id, language=int(data["language"]),
                                                   code=data["code"], problem_id=problem.id)

            try:
                judge.delay(submission.id, problem.time_limit, problem.memory_limit, problem.test_case_id)
            except Exception:
                return error_response(u"提交判题任务失败")

            # 增加redis 中判题队列长度的计数器
            r = redis.Redis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
            r.incr("judge_queue_length")

            return success_response({"submission_id": submission.id})
        else:
            return serializer_invalid_response(serializer)

    @login_required
    def get(self, request):
        submission_id = request.GET.get("submission_id", None)
        if not submission_id:
            return error_response(u"参数错误")
        try:
            submission = Submission.objects.get(id=submission_id, user_id=request.user.id)
        except Submission.DoesNotExist:
            return error_response(u"提交不存在")
        response_data = {"result": submission.result}
        if submission.result == 0:
            response_data["accepted_answer_time"] = submission.accepted_answer_time
        return success_response(response_data)


@login_required
def problem_my_submissions_list_page(request, problem_id):
    """
    我单个题目所有提交的列表页
    """
    try:
        problem = Problem.objects.get(id=problem_id, visible=True)
    except Problem.DoesNotExist:
        return error_page(request, u"问题不存在")

    submissions = Submission.objects.filter(user_id=request.user.id, problem_id=problem.id, contest_id__isnull=True).order_by("-create_time"). \
        values("id", "result", "create_time", "accepted_answer_time", "language")

    return render(request, "oj/problem/my_submissions_list.html",
                  {"submissions": submissions, "problem": problem})


@login_required
def my_submission(request, submission_id):
    """
    单个题目的提交详情页
    """
    try:
        # 超级管理员可以查看所有的提交
        if request.user.admin_type != SUPER_ADMIN:
            submission = Submission.objects.get(id=submission_id, user_id=request.user.id)
        else:
            submission = Submission.objects.get(id=submission_id)
    except Submission.DoesNotExist:
        return error_page(request, u"提交不存在")

    if submission.contest_id:
        try:
            problem = ContestProblem.objects.get(id=submission.problem_id,
                                                 visible=True)
        except ContestProblem.DoesNotExist:
            return error_page(request, u"提交不存在")
    else:
        try:
            problem = Problem.objects.get(id=submission.problem_id, visible=True)
        except Problem.DoesNotExist:
            return error_page(request, u"提交不存在")

    if submission.info:
        try:
            info = json.loads(submission.info)
        except Exception:
            info = submission.info
    else:
        info = None
    return render(request, "oj/problem/my_submission.html",
                  {"submission": submission, "problem": problem, "info": info})


class SubmissionAdminAPIView(APIView):
    def get(self, request):
        problem_id = request.GET.get("problem_id", None)
        if not problem_id:
            return error_response(u"参数错误")
        submissions = Submission.objects.filter(problem_id=problem_id).order_by("-create_time")
        return paginate(request, submissions, SubmissionSerializer)


@login_required
def my_submission_list_page(request, page=1):
    """
    我的所有提交的列表页
    """
    submissions = Submission.objects.filter(user_id=request.user.id, contest_id__isnull=True). \
        values("id", "result", "create_time", "accepted_answer_time", "language").order_by("-create_time")
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

    return render(request, "oj/submission/my_submissions_list.html",
                  {"submissions": current_page, "page": int(page),
                   "previous_page": previous_page, "next_page": next_page, "start_id": int(page) * 20 - 20,
                   "announcements": announcements, "filter":filter})