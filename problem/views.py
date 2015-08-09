# coding=utf-8
import json
from django.shortcuts import render

from rest_framework.views import APIView

from django.db.models import Q

from serizalizers import CreateProblemSerializer, EditProblemSerializer, ProblemSerializer
from .models import Problem, ProblemTag
from utils.shortcuts import serializer_invalid_response, error_response, success_response, paginate


def problem_page(request, problem_id):
    # todo
    return render(request, "oj/problem/problem.html")


class ProblemAdminAPIView(APIView):
    def post(self, request):
        """
        题目发布json api接口
        ---
        request_serializer: CreateProblemSerializer
        response_serializer: ProblemSerializer
        """
        serializer = CreateProblemSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            problem = Problem.objects.create(title=data["title"],
                                             description=data["description"],
                                             test_case_id=data["test_case_id"],
                                             source=data["source"],
                                             sample=json.dumps(data["sample"]),
                                             time_limit=data["time_limit"],
                                             memory_limit=data["memory_limit"],
                                             difficulty=data["difficulty"],
                                             created_by=request.user,
                                             hint=data["hint"])

            tags = ProblemTag.objects.filter(id__in=data["tags"])
            problem.tags.add(*tags)
            return success_response(ProblemSerializer(problem).data)
        else:
            return serializer_invalid_response(serializer)

    def put(self, request):
        """
        题目编辑json api接口
        ---
        request_serializer: EditProblemSerializer
        response_serializer: ProblemSerializer
        """
        serializer = EditProblemSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            print request.data
            try:
                problem = Problem.objects.get(id=data["id"])
            except Problem.DoesNotExist:
                return error_response(u"该题目不存在！")

            problem.title = data["title"]
            problem.description = data["description"]
            problem.test_case_id = data["test_case_id"]
            problem.source = data["source"]
            problem.time_limit = data["time_limit"]
            problem.memory_limit = data["memory_limit"]
            problem.difficulty = data["difficulty"]
            problem.sample = json.dumps(data["sample"])
            problem.hint = data["hint"]
            problem.visible = data["visible"]

            # 删除原有的标签的对应关系
            problem.tags.remove(*problem.tags.all())
            # 重新添加所有的标签
            problem.tags.add(*ProblemTag.objects.filter(id__in=data["tags"]))
            problem.save()
            return success_response(ProblemSerializer(problem).data)
        else:
            return serializer_invalid_response(serializer)


class ProblemAPIView(APIView):
    def get(self, request):
        """
        题目分页json api接口
        ---
        response_serializer: ProblemSerializer
        """
        problem = Problem.objects.all().order_by("-last_update_time")
        visible = request.GET.get("visible", None)
        if visible:
            problem = problem.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            problem = problem.filter(Q(difficulty__contains=keyword))

        return paginate(request, problem, ProblemSerializer)
