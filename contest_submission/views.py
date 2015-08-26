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

from contest.decorators import check_user_contest_permission

from problem.models import Problem
from contest.models import Contest, ContestProblem

from utils.shortcuts import serializer_invalid_response, error_response, success_response, error_page, paginate

from submission.models import Submission
from .serializers import CreateContestSubmissionSerializer


class ContestSubmissionAPIView(APIView):
    @check_user_contest_permission
    def post(self, request):
        """
        创建比赛的提交
        ---
        request_serializer: CreateContestSubmissionSerializer
        """
        serializer = CreateContestSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            contest = Contest.objects.get(id=data["contest_id"])
            try:
                problem = ContestProblem.objects.get(contest=contest, id=data["problem_id"])
                # 更新题目提交计数器
                problem.total_submit_number += 1
                problem.save()
            except ContestProblem.DoesNotExist:
                return error_response(u"题目不存在")

            submission = Submission.objects.create(user_id=request.user.id, language=int(data["language"]),
                                                   contest_id=contest.id, code=data["code"], problem_id=problem.id)
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
    submissions = Submission.objects.filter(user_id=request.user.id, problem_id=contest_problem.id).order_by("-create_time"). \
        values("id", "result", "create_time", "accepted_answer_time", "language")
    return render(request, "oj/contest/my_submissions_list.html",
                  {"submissions": submissions, "problem": contest_problem})


@login_required
def contest_problem_submissions_list_page(request, contest_id, page=1):
    """
    单个比赛中的所有提交（包含自己和别人，自己可查提交结果，其他人不可查）
    """
    try:
        contest = Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return error_page(request, u"比赛不存在")
    # 以下是本场比赛中所有的提交
    submissions = Submission.objects.filter(contest_id=contest_id). \
        values("id", "result", "create_time", "accepted_answer_time", "language", "user_id").order_by("-create_time")
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

    return render(request, "oj/contest/submissions_list.html",
                  {"submissions": current_page, "page": int(page),
                   "previous_page": previous_page, "next_page": next_page, "start_id": int(page) * 20 - 20,
                   "contest": contest})