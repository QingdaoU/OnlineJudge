# coding=utf-8
import zipfile
import re
import os
import hashlib
import json

from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator

from rest_framework.views import APIView

from django.conf import settings

from announcement.models import Announcement
from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, paginate, rand_str, error_page)
from .serizalizers import (CreateProblemSerializer, EditProblemSerializer, ProblemSerializer,
                           ProblemTagSerializer, CreateProblemTagSerializer)
from .models import Problem, ProblemTag


def problem_page(request, problem_id):
    try:
        problem = Problem.objects.get(id=problem_id, visible=True)
    except Problem.DoesNotExist:
        return error_page(request, u"题目不存在")
    return render(request, "oj/problem/problem.html", {"problem": problem, "samples": json.loads(problem.samples)})


class ProblemTagAdminAPIView(APIView):
    def get(self, request):
        return success_response(ProblemTagSerializer(ProblemTag.objects.all(), many=True).data)


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
                                             input_description=data["input_description"],
                                             output_description=data["output_description"],
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
            problem.input_description = data["input_description"]
            problem.output_description = data["output_description"]
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
            for tag in data["tags"]:
                try:
                    tag = ProblemTag.objects.get(name=tag)
                except ProblemTag.DoesNotExist:
                    tag = ProblemTag.objects.create(name=tag)
                problem.tags.add(tag)
            problem.save()
            return success_response(ProblemSerializer(problem).data)
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        题目分页json api接口
        ---
        response_serializer: ProblemSerializer
        """
        problem_id = request.GET.get("problem_id", None)
        if problem_id:
            try:
                problem = Problem.objects.get(id=problem_id)
                return success_response(ProblemSerializer(problem).data)
            except Problem.DoesNotExist:
                return error_response(u"题目不存在")
        problem = Problem.objects.all().order_by("-create_time")
        visible = request.GET.get("visible", None)
        if visible:
            problem = problem.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            problem = problem.filter(Q(title__contains=keyword) |
                                     Q(description__contains=keyword))

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

        tmp_zip = "/tmp/" + rand_str() + ".zip"
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
            test_case_dir = settings.TEST_CASE_DIR + problem_test_dir + "/"

            # 得到了合法的测试用例文件列表 然后去解压缩
            os.mkdir(test_case_dir)
            for name in l:
                f = open(test_case_dir + name, "wb")
                try:
                    f.write(test_case_file.read(name).replace("\r\n", "\n"))
                except MemoryError:
                    return error_response(u"单个测试数据体积过大!")
                finally:
                    f.close()
            l.sort()

            file_info = {"test_case_number": len(l) / 2, "test_cases": {}}

            # 计算输出文件的md5
            for i in range(len(l) / 2):
                md5 = hashlib.md5()
                striped_md5 = hashlib.md5()
                f = open(test_case_dir + str(i + 1) + ".out", "r")
                # 完整文件的md5
                while True:
                    data = f.read(2 ** 8)
                    if not data:
                        break
                    md5.update(data)

                # 删除标准输出最后的空格和换行
                # 这时只能一次全部读入了，分块读的话，没办法确定文件结尾
                f.seek(0)
                striped_md5.update(f.read().rstrip())

                file_info["test_cases"][str(i + 1)] = {"input_name": str(i + 1) + ".in",
                                                       "output_name": str(i + 1) + ".out",
                                                       "output_md5": md5.hexdigest(),
                                                       "striped_output_md5": striped_md5.hexdigest(),
                                                       "output_size": os.path.getsize(test_case_dir + str(i + 1) + ".out")}
                # 写入配置文件
                open(test_case_dir + "info", "w").write(json.dumps(file_info))

            return success_response({"test_case_id": problem_test_dir,
                                     "file_list": {"input": l[0::2],
                                                   "output": l[1::2]}})
        else:
            return error_response(u"测试用例压缩文件格式错误，请保证测试用例文件在根目录下直接压缩")


def problem_list_page(request, page=1):
    # 正常情况
    problems = Problem.objects.filter(visible=True)

    # 搜索的情况
    keyword = request.GET.get("keyword", None)
    if keyword:
        problems = problems.filter(Q(title__contains=keyword) | Q(description__contains=keyword))

    difficulty_order = request.GET.get("order_by", None)
    if difficulty_order:
        if difficulty_order[0] == "-":
            problems = problems.order_by("-difficulty")
            difficulty_order = "difficulty"
        else:
            problems = problems.order_by("difficulty")
            difficulty_order = "-difficulty"
    else:
        difficulty_order = "difficulty"

    # 按照标签筛选
    tag_text = request.GET.get("tag", None)
    if tag_text:
        try:
            tag = ProblemTag.objects.get(name=tag_text)
        except ProblemTag.DoesNotExist:
            return error_page(request, u"标签不存在")
        problems = tag.problem_set.all()

    paginator = Paginator(problems, 20)
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

    # 右侧标签列表 按照关联的题目的数量排序 排除题目数量为0的
    tags = ProblemTag.objects.annotate(problem_number=Count("problem")).filter(problem_number__gt=0).order_by("-problem_number")

    return render(request, "oj/problem/problem_list.html",
                  {"problems": current_page, "page": int(page),
                   "previous_page": previous_page, "next_page": next_page,
                   "keyword": keyword, "tag": tag_text,
                   "tags": tags, "difficulty_order": difficulty_order})
