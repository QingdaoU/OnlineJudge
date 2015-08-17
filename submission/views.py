# coding=utf-8
import json

from django.shortcuts import render

from rest_framework.views import APIView

from judge.judger.result import result
from judge.judger_controller.tasks import judge
from account.decorators import login_required
from problem.models import Problem
from utils.shortcuts import serializer_invalid_response, error_response, success_response, error_page
from .models import Submission
from .serializers import CreateSubmissionSerializer


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
            except Problem.DoesNotExist:
                return error_response(u"题目不存在")
            submission = Submission.objects.create(user_id=request.user.id, language=int(data["language"]),
                                                   code=data["code"], problem_id=problem.id)

            try:
                judge.delay(submission.id, problem.time_limit, problem.memory_limit, problem.test_case_id)
            except Exception:
                return error_response(u"提交判题任务失败")

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
    try:
        problem = Problem.objects.get(id=problem_id, visible=True)
    except Problem.DoesNotExist:
        return error_page(request, u"问题不存在")
    submissions = Submission.objects.filter(user_id=request.user.id, problem_id=problem.id).order_by("-create_time")
    return render(request, "oj/problem/my_submissions_list.html",
                  {"submissions": submissions, "problem": problem})


@login_required
def my_submission(request, submission_id):
    try:
        submission = Submission.objects.get(id=submission_id)
    except Submission.DoesNotExist:
        return error_page(request, u"提交不存在")
    try:
        problem = Problem.objects.get(id=submission.problem_id, visible=True)
    except Problem.DoesNotExist:
        return error_page(request, u"提交不存在")
    return render(request, "oj/problem/my_submission.html",
                  {"submission": submission, "problem": problem})