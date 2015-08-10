# coding=utf-8
import zipfile
import re
import os
import hashlib
import json

from django.shortcuts import render
from django.db.models import Q

from rest_framework.views import APIView

from utils.shortcuts import serializer_invalid_response, error_response, success_response, paginate, rand_str
from .serizalizers import (CreateProblemSerializer, EditProblemSerializer, ProblemSerializer,
                           ProblemTagSerializer, CreateProblemTagSerializer)
from .models import Problem, ProblemTag


class ProblemTagAdminAPIView(APIView):
    def post(self, request):
        """
        创建标签的接口
        ---
        request_serializer: CreateProblemTagSerializer
        """
        serializer = CreateProblemTagSerializer(data=request.data)
        if serializer.is_valid():
            try:
                tag = ProblemTag.objects.get(name=serializer.data["name"])
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=serializer.data["name"])
            return success_response(ProblemTagSerializer(tag).data)
        else:
            return error_response(serializer)

    def get(self, request):
        return success_response(ProblemTagSerializer(ProblemTag.objects.all(), many=True).data)
        keyword = request.GET.get("keyword", None)
        if not keyword:
            return error_response(u"参数错误")
        tags = ProblemTag.objects.filter(name__contains=keyword)
        return success_response(ProblemTagSerializer(tags, many=True).data)




def problem_page(request, problem_id):
    try:
        problem = Problem.objects.get(id=problem_id)
    except Problem.DoesNotExist:
        return render(request, "utils/error.html", {"error": u"题目不存在"})
    return render(request, "oj/problem/problem.html", {"problem": problem, "samples": json.loads(problem.samples)})


def problem_my_solutions_list_page(request, problem_id):
    return render(request, "oj/problem/my_solutions_list.html")


def my_solution(request, solution_id):
    return render(request, "oj/problem/my_solution.html")



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
                                             samples=json.dumps(data["samples"]),
                                             time_limit=data["time_limit"],
                                             memory_limit=data["memory_limit"],
                                             difficulty=data["difficulty"],
                                             created_by=request.user,
                                             hint=data["hint"])

            for tag in data["tags"]:
                try:
                    tag = ProblemTag.objects.get(name=tag)
                except ProblemTag.DoesNotExist:
                    tag = ProblemTag.objects.create(name=tag)
                problem.tags.add(tag)
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
            problem.samples = json.dumps(data["samples"])
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


class TestCaseUploadAPIView(APIView):
    def _is_legal_test_case_file_name(self, file_name):
        # 正整数开头的 .in 或者.out 结尾的
        regex = r"^[1-9]\d*\.(in|out)$"
        return re.compile(regex).match(file_name) is not None

    def post(self, request):
        if "file" not in request.FILES:
            return error_response(u"文件上传失败")

        f = request.FILES["file"]

        tmp_zip = "tmp/" + rand_str() + ".zip"
        with open(tmp_zip, "wb") as test_case_zip:
            for chunk in f:
                test_case_zip.write(chunk)

        test_case_file = zipfile.ZipFile(tmp_zip, 'r')
        name_list = test_case_file.namelist()

        l = []

        # 如果文件是直接打包的，那么name_list 就是["1.in", "1.out"]这样的
        # 如果文件还有一层文件夹test_case，那么name_list就是["test_case/", "test_case/1.in", "test_case/1.out"]
        # 现在暂时只支持第一种，先判断一下是什么格式的

        # 第一种格式的
        if "1.in" in name_list and "1.out" in name_list:
            for file_name in name_list:
                if self._is_legal_test_case_file_name(file_name):
                    name = file_name.split(".")
                    # 有了.in 判断对应的.out 在不在
                    if name[1] == "in":
                        if (name[0] + ".out") in name_list:
                            l.append(file_name)
                        else:
                            return error_response(u"测试用例文件不完整，缺少" + name[0] + ".out")
                    else:
                        # 有了.out 判断对应的 .in 在不在
                        if (name[0] + ".in") in name_list:
                            l.append(file_name)
                        else:
                            return error_response(u"测试用例文件不完整，缺少" + name[0] + ".in")

            problem_test_dir = rand_str()
            test_case_dir = "test_case/" + problem_test_dir + "/"

            # 得到了合法的测试用例文件列表 然后去解压缩
            os.mkdir(test_case_dir)
            for name in l:
                f = open(test_case_dir + name, "wb")
                f.write(test_case_file.read(name))
                f.close()
            l.sort()

            file_info = {"test_case_number": len(l) / 2, "test_cases": {}}

            # 计算输出文件的md5
            for i in range(len(l) / 2):
                md5 = hashlib.md5()
                f = open(test_case_dir + str(i + 1) + ".out", "r")
                while True:
                    data = f.read(2 ** 8)
                    if not data:
                        break
                    md5.update(data)

                file_info["test_cases"][str(i + 1)] = {"input_name": str(i + 1) + ".in",
                                                       "output_name": str(i + 1) + ".out",
                                                       "output_md5": md5.hexdigest(),
                                                       "output_size": os.path.getsize(test_case_dir + str(i + 1) + ".out")}
                # 写入配置文件
                open(test_case_dir + "info", "w").write(json.dumps(file_info))

            return success_response({"test_case_id": problem_test_dir,
                                     "file_list": {"input": l[0::2],
                                                   "output": l[1::2]}})
        else:
            return error_response(u"测试用例压缩文件格式错误，请保证测试用例文件在根目录下直接压缩")