# coding=utf-8
import pymongo
from bson.objectid import ObjectId

from django.shortcuts import render

from rest_framework.views import APIView

from django.conf import settings

from judge.judger.result import result
from judge.controller.tasks import judge
from account.decorators import login_required
from problem.models import Problem
from utils.shortcuts import serializer_invalid_response, error_response, success_response
from .serializers import  CreateSubmissionSerializer


class SubmissionnAPIView(APIView):
    def _create_mondodb_connection(self):
        mongodb_setting = settings.DATABASES["mongodb"]
        connection = pymongo.MongoClient(host=mongodb_setting["HOST"], port=mongodb_setting["PORT"])
        return connection["oj"]["oj_submission"]

    # @login_required
    def post(self, request):
        """
        提交代码
        ---
        request_serializer: CreateSubmissionSerializer
        """
        serializer = CreateSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            data["user_id"] = request.user.id
            data["result"] = result["waiting"]
            try:
                problem = Problem.objects.get(id=data["problem_id"])
            except Problem.DoesNotExist:
                return error_response(u"题目不存在")
            mongodb_setting = settings.DATABASES["mongodb"]
            connection = pymongo.MongoClient(host=mongodb_setting["HOST"], port=mongodb_setting["PORT"])
            collection = connection["oj"]["oj_submission"]
            submission_id = str(collection.insert_one(data).inserted_id)
            judge.deply(submission_id, problem.max_cpu_time, problem_)
            return success_response({"submission_id": submission_id})
        else:
            return serializer_invalid_response(serializer)

    # @login_required
    def get(self, request):
        submission_id = request.GET.get("submission_id", None)
        if not submission_id:
            return error_response(u"参数错误")
        submission = self._create_mondodb_connection().find_one({"_id": ObjectId(submission_id), "user_id": result.user.id})
        if submission:
            return success_response({"result": submission["result"]})
        else:
            return error_response(u"提交不存在")
