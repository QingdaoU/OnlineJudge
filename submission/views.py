# coding=utf-8
import datetime
import pymongo
from bson.objectid import ObjectId

from django.shortcuts import render

from rest_framework.views import APIView

from django.conf import settings

from judge.judger.result import result
from judge.judger_controller.tasks import judge
from account.decorators import login_required
from problem.models import Problem
from utils.shortcuts import serializer_invalid_response, error_response, success_response, error_page
from .serializers import CreateSubmissionSerializer


def _create_mongodb_connection():
    mongodb_setting = settings.MONGODB
    connection = pymongo.MongoClient(host=mongodb_setting["HOST"], port=mongodb_setting["PORT"])
    return connection["oj"]["oj_submission"]


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
            # data["language"] = int(data["language"])
            data["user_id"] = request.user.id
            data["result"] = result["waiting"]
            data["create_time"] = datetime.datetime.now()
            try:
                problem = Problem.objects.get(id=data["problem_id"])
            except Problem.DoesNotExist:
                return error_response(u"题目不存在")
            collection = _create_mongodb_connection()
            submission_id = str(collection.insert_one(data).inserted_id)
            judge.delay(submission_id, problem.time_limit, problem.memory_limit, problem.test_case_id)
            return success_response({"submission_id": submission_id})
        else:
            return serializer_invalid_response(serializer)

    @login_required
    def get(self, request):
        submission_id = request.GET.get("submission_id", None)
        if not submission_id:
            return error_response(u"参数错误")
        submission = _create_mongodb_connection().find_one({"_id": ObjectId(submission_id), "user_id": request.user.id})
        if submission:
            response_data = {"result": submission["result"]}
            if submission["result"] == 0:
                response_data["accepted_answer_info"] = submission["accepted_answer_info"]
            return success_response(response_data)
        else:
            return error_response(u"提交不存在")


@login_required
def problem_my_submissions_list_page(request, problem_id):
    collection = _create_mongodb_connection()
    submissions = collection.find({"problem_id": int(problem_id), "user_id": request.user.id},
                                  projection=["result", "accepted_answer_info", "create_time", "language"],
                                  sort=[["create_time", -pymongo.ASCENDING]])
    try:
        problem = Problem.objects.get(id=problem_id, visible=True)
    except Problem.DoesNotExist:
        return error_page(request, u"问题不存在")
    return render(request, "oj/problem/my_submissions_list.html",
                  {"submissions": submissions, "problem": problem})


@login_required
def my_submission(request, submission_id):
    collection = _create_mongodb_connection()
    submission = collection.find_one({"user_id": request.user.id, "_id": ObjectId(submission_id)},
                                     projection=["result", "accepted_answer_info", "create_time",
                                                 "language", "code", "problem_id", "info"])
    if not submission:
        return error_page(request, u"提交不存在")
    try:
        problem = Problem.objects.get(id=submission["problem_id"], visible=True)
    except Problem.DoesNotExist:
        return error_page(request, u"提交不存在")

    return render(request, "oj/problem/my_submission.html", {"submission": submission, "problem": problem})