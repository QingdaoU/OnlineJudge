# coding=utf-8
import json

import redis
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from rest_framework.views import APIView
from rest_framework.test import APITestCase, APIClient

from judge.judger_controller.tasks import judge
from judge.judger_controller.settings import redis_config
from account.decorators import login_required
from account.models import User, ADMIN, SUPER_ADMIN

from contest.decorators import check_user_contest_permission

from problem.models import Problem
from contest.models import Contest, ContestProblem

from utils.shortcuts import serializer_invalid_response, error_response, success_response, error_page, paginate

from submission.models import Submission
from .serializers import CreateContestSubmissionSerializer
from submission.serializers import SubmissionSerializer


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
    submissions = Submission.objects.filter(user_id=request.user.id, problem_id=contest_problem.id).order_by(
        "-create_time"). \
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


class ContestSubmissionAdminAPIView(APIView):
    def get(self, request):
        """
        查询比赛提交,单个比赛题目提交的adminAPI
        ---
        response_serializer: SubmissionSerializer
        """
        problem_id = request.GET.get("problem_id", None)
        contest_id = request.GET.get("contest_id", None)
        if contest_id:
            try:
                contest = Contest.objects.get(pk=contest_id)
            except Contest.DoesNotExist:
                return error_response(u"比赛不存在!")
            if request.user.admin_type != SUPER_ADMIN and contest.created_by != request.user:
                return error_response(u"您无权查看该信息!")
            submissions = Submission.objects.filter(contest_id=contest_id).order_by("-create_time")
        else:
            if problem_id:
                try:
                    contest_problem = ContestProblem.objects.get(pk=problem_id)
                except ContestProblem.DoesNotExist:
                    return error_response(u"问题不存在!")
                if request.user.admin_type != SUPER_ADMIN and contest_problem.contest.created_by != request.user:
                    return error_response(u"您无权查看该信息!")
                submissions = Submission.objects.filter(contest_id=contest_problem.contest_id).order_by("-create_time")
            else:
                return error_response(u"参数错误!")
        if problem_id:
            submissions = submissions.filter(problem_id=problem_id)

        return paginate(request, submissions, SubmissionSerializer)


class SubmissionAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contest_submission_admin_api_view')
        self.userA = User.objects.create(username="test1", admin_type=ADMIN)
        self.userA.set_password("testaa")
        self.userA.save()
        self.userS = User.objects.create(username="test2", admin_type=SUPER_ADMIN)
        self.userS.set_password("testbb")
        self.userS.save()
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=2, show_rank=True, show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=self.userS
                                                     )
        self.problem = ContestProblem.objects.create(title="title1",
                                                     description="description1",
                                                     input_description="input1_description",
                                                     output_description="output1_description",
                                                     test_case_id="1",
                                                     sort_index="1",
                                                     samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                                     time_limit=100,
                                                     memory_limit=1000,
                                                     hint="hint1",
                                                     contest=self.global_contest,
                                                     created_by=self.userS)
        self.submission = Submission.objects.create(user_id=self.userA.id,
                                                    language=1,
                                                    code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                    problem_id=self.problem.id)
        self.submissionS = Submission.objects.create(user_id=self.userS.id,
                                                     language=2,
                                                     code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                     problem_id=self.problem.id)

    def test_submission_contest_does_not_exist(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url + "?contest_id=99")
        self.assertEqual(response.data["code"], 1)

    def test_submission_contest_parameter_error(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url)
        self.assertEqual(response.data["code"], 1)

    def test_submission_access_denied(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?problem_id=" + str(self.problem.id))
        self.assertEqual(response.data["code"], 1)

    def test_submission_access_denied_with_contest_id(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?contest_id=" + str(self.global_contest.id))
        self.assertEqual(response.data["code"], 1)

    def test_get_submission_successfully(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(
            self.url + "?contest_id=" + str(self.global_contest.id) + "&problem_id=" + str(self.problem.id))
        self.assertEqual(response.data["code"], 0)

    def test_get_submission_successfully_problem(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url + "?problem_id=" + str(self.problem.id))
        self.assertEqual(response.data["code"], 0)

    def test_get_submission_problem_do_not_exist(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url + "?problem_id=9999")
        self.assertEqual(response.data["code"], 1)
