# coding=utf-8
import zipfile
import re
import os
import hashlib
import json
import logging

from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.conf import settings
from rest_framework.views import APIView

from account.models import SUPER_ADMIN, User
from account.decorators import super_admin_required, admin_required
from contest.models import ContestProblem
from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, paginate, rand_str, error_page)
from .serizalizers import (CreateProblemSerializer, EditProblemSerializer, ProblemSerializer,
                           ProblemTagSerializer, OpenAPIProblemSerializer)
from .models import Problem, ProblemTag
from .decorators import check_user_problem_permission

logger = logging.getLogger("app_info")


def problem_page(request, problem_id):
    """
    前台题目详情页
    """
    try:
        problem = Problem.objects.get(id=problem_id, visible=True)
    except Problem.DoesNotExist:
        return error_page(request, u"题目不存在")
    return render(request, "oj/problem/problem.html", {"problem": problem, "samples": json.loads(problem.samples)})


class OpenAPIProblemAPI(APIView):
    def get(sell, request):
        """
        openapi 获取题目内容
        """
        problem_id = request.GET.get("problem_id", None)
        appkey = request.GET.get("appkey", None)
        if not (problem_id and appkey):
            return error_response(u"参数错误")
        try:
            User.objects.get(openapi_appkey=appkey)
        except User.DoesNotExist:
            return error_response(u"appkey无效")
        try:
            problem = Problem.objects.get(id=problem_id, visible=True)
        except Problem.DoesNotExist:
            return error_page(request, u"题目不存在")
        return success_response(OpenAPIProblemSerializer(problem).data)


class ProblemTagAdminAPIView(APIView):
    """
    获取所有标签的列表
    """

    def get(self, request):
        return success_response(ProblemTagSerializer(ProblemTag.objects.all(), many=True).data)


class ProblemAdminAPIView(APIView):
    def _spj_version(self, code):
        if code is None:
            return None
        return hashlib.md5(code.encode("utf-8")).hexdigest()

    @super_admin_required
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
            try:
                Problem.objects.get(title=data["title"])
                return error_response(u"添加失败，存在重复的题目")
            except Problem.DoesNotExist:
                pass
            problem = Problem.objects.create(title=data["title"],
                                             description=data["description"],
                                             input_description=data["input_description"],
                                             output_description=data["output_description"],
                                             test_case_id=data["test_case_id"],
                                             source=data["source"],
                                             samples=json.dumps(data["samples"]),
                                             time_limit=data["time_limit"],
                                             memory_limit=data["memory_limit"],
                                             spj=data["spj"],
                                             spj_language=data["spj_language"],
                                             spj_code=data["spj_code"],
                                             spj_version=self._spj_version(data["spj_code"]),
                                             difficulty=data["difficulty"],
                                             created_by=request.user,
                                             hint=data["hint"],
                                             visible=data["visible"])
            for tag in data["tags"]:
                try:
                    tag = ProblemTag.objects.get(name=tag)
                except ProblemTag.DoesNotExist:
                    tag = ProblemTag.objects.create(name=tag)
                problem.tags.add(tag)
            return success_response(ProblemSerializer(problem).data)
        else:
            return serializer_invalid_response(serializer)

    @check_user_problem_permission
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
            problem = Problem.objects.get(id=data["id"])

            problem.title = data["title"]
            problem.description = data["description"]
            problem.input_description = data["input_description"]
            problem.output_description = data["output_description"]
            problem.test_case_id = data["test_case_id"]
            problem.source = data["source"]
            problem.time_limit = data["time_limit"]
            problem.memory_limit = data["memory_limit"]
            problem.spj = data["spj"]
            problem.spj_language = data["spj_language"]
            problem.spj_code = data["spj_code"]
            problem.spj_version = self._spj_version(data["spj_code"])
            problem.difficulty = data["difficulty"]
            problem.samples = json.dumps(data["samples"])
            problem.hint = data["hint"]
            problem.visible = data["visible"]
            problem.last_update_time = now()

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
                # 普通管理员只能获取自己创建的题目
                # 超级管理员可以获取全部的题目
                problem = Problem.objects.get(id=problem_id)
                if request.user.admin_type != SUPER_ADMIN and problem.created_by != request.user:
                    return error_response(u"题目不存在")
                return success_response(ProblemSerializer(problem).data)
            except Problem.DoesNotExist:
                return error_response(u"题目不存在")

        # 获取问题列表
        problems = Problem.objects.all().order_by("-create_time")

        if request.user.admin_type != SUPER_ADMIN:
            problems = problems.filter(created_by=request.user)

        visible = request.GET.get("visible", None)
        if visible:
            problems = problems.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            problems = problems.filter(Q(title__contains=keyword) |
                                       Q(description__contains=keyword))

        return paginate(request, problems, ProblemSerializer)


class TestCaseUploadAPIView(APIView):
    """
    上传题目的测试用例
    """

    def _is_legal_test_case_file_name(self, file_name):
        # 正整数开头的 .in 或者.out 结尾的
        regex = r"^[1-9]\d*\.(in|out)$"
        return re.compile(regex).match(file_name) is not None

    def post(self, request):
        if "file" not in request.FILES:
            return error_response(u"文件上传失败")

        f = request.FILES["file"]

        tmp_zip = "/tmp/" + rand_str() + ".zip"
        try:
            with open(tmp_zip, "wb") as test_case_zip:
                for chunk in f:
                    test_case_zip.write(chunk)
        except IOError as e:
            logger.error(e)
            return error_response(u"上传失败")
        try:
            test_case_file = zipfile.ZipFile(tmp_zip, 'r')
        except Exception:
            return error_response(u"解压失败")
        name_list = test_case_file.namelist()

        # 如果文件是直接打包的，那么name_list 就是["1.in", "1.out"]这样的
        if len(name_list) == 0:
            return error_response(u"压缩包内没有文件")

        for item in name_list:
            if not self._is_legal_test_case_file_name(item):
                return error_response(u"%s 文件名不符合规范" % item)

        # 排序,这样name_list就是[1.in, 1.out, 2.in, 2.out]的形式了
        name_list.sort()

        spj = False

        for item in name_list:
            # 代表里面有.out文件,所以应该是普通题目的测试用例
            if item.endswith(".out"):
                break
        else:
            # 否则就应该是spj的测试用例
            spj = True

        if not spj:
            if len(name_list) % 2 == 1:
                return error_response(u"测试用例文件格式错误，文件数目为奇数")

            for index in range(1, len(name_list) / 2 + 1):
                if not (str(index) + ".in" in name_list and str(index) + ".out" in name_list):
                    return error_response(u"测试用例文件格式错误，缺少" + str(index) + u".in/.out文件")
            test_case_number = len(name_list) / 2
        else:
            for index in range(1, len(name_list) + 1):
                if str(index) + ".in" not in name_list:
                    return error_response(u"测试用例文件格式错误，缺少" + str(index) + u".in文件")
            test_case_number = len(name_list)

        problem_test_dir = rand_str()
        test_case_dir = os.path.join(settings.TEST_CASE_DIR, problem_test_dir)

        # 得到了合法的测试用例文件列表 然后去解压缩
        os.mkdir(test_case_dir)
        for name in name_list:
            f = open(os.path.join(test_case_dir, name), "wb")
            try:
                f.write(test_case_file.read(name).replace("\r\n", "\n"))
            except MemoryError:
                return error_response(u"单个测试数据体积过大!")
            finally:
                f.close()

        file_info = {"test_case_number": test_case_number, "test_cases": {}, "spj": spj}

        # 计算输出文件的md5
        for i in range(1, test_case_number + 1):
            if not spj:
                md5 = hashlib.md5()
                striped_md5 = hashlib.md5()
                f = open(os.path.join(test_case_dir, str(i) + ".out"), "r")
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

                output_md5 = md5.hexdigest()
                striped_output_md5 = striped_md5.hexdigest()
                output_name = str(i) + ".out"
                output_size = os.path.getsize(os.path.join(test_case_dir, output_name))
            else:
                output_md5 = striped_output_md5 = output_name = output_size = None

            file_info["test_cases"][str(i)] = {"input_name": str(i) + ".in",
                                               "output_name": output_name,
                                               "output_md5": output_md5,
                                               "striped_output_md5": striped_output_md5,
                                               "input_size": os.path.getsize(os.path.join(test_case_dir, str(i) + ".in")),
                                               "output_size": output_size}
            # 写入配置文件
        with open(os.path.join(test_case_dir, "info"), "w") as f:
            f.write(json.dumps(file_info))

        return success_response({"test_case_id": problem_test_dir,
                                 "file_list": file_info["test_cases"],
                                 "spj": spj})

    def get(self, request):
        test_case_id = request.GET.get("test_case_id", None)
        if not test_case_id:
            return error_response(u"参数错误")
        test_case_config = os.path.join(settings.TEST_CASE_DIR, test_case_id, "info")
        try:
            f = open(test_case_config)
            config = json.loads(f.read())
            f.close()
        except Exception as e:
            return error_response(u"读取测试用例出错")
        return success_response({"file_list": config["test_cases"], "spj": config.get("spj", False)})


class TestCaseDownloadAPIView(APIView):
    """
    下载题目的测试数据
    """

    def _is_legal_test_case_file_name(self, file_name):
        regex = r"^[1-9]\d*\.(in|out)$"
        return re.compile(regex).match(file_name) is not None

    def file_iterator(self, big_file, chunk_size=512):
        with open(big_file) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    @admin_required
    def get(self, request):
        test_case_id = request.GET.get("test_case_id", None)
        if not test_case_id:
            return error_response(u"参数错误")
        # 防止URL./../../.上层目录遍历
        if not re.compile(r"^[0-9a-zA-Z]+$").match(test_case_id):
            return error_response(u"参数错误")

        try:
            # 超级管理员可以下载全部的题目的测试数据
            # 普通管理员只能下载自己创建的题目的测试数据
            if request.user.admin_type != SUPER_ADMIN:
                ContestProblem.objects.get(test_case_id=test_case_id, created_by=request.user)

            test_case_dir = os.path.join(settings.TEST_CASE_DIR, test_case_id)
            if not os.path.exists(test_case_dir):
                return error_response(u"测试用例不存在")

            # 压缩测试用例,命名规则为 "test_case" + test_case_id + ".zip"
            test_case_zip = os.path.join("/tmp", "test_case-" + test_case_id + ".zip")

            zf = zipfile.ZipFile(test_case_zip, "w", zipfile.ZIP_DEFLATED)
            for filename in os.listdir(test_case_dir):
                # 避免存在文件链接,导致真实文件被打包
                if self._is_legal_test_case_file_name(filename) and not os.path.islink(os.path.join(test_case_dir, filename)):
                    zf.write(os.path.join(test_case_dir, filename), filename)
            zf.close()

            # 大文件传输
            response = StreamingHttpResponse(self.file_iterator(test_case_zip))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=test_case-%s.zip' % test_case_id
            return response
        except ContestProblem.DoesNotExist:
            return error_response(u"题目不存在")


def problem_list_page(request, page=1):
    """
    前台的问题列表
    """
    # 正常情况
    problems = Problem.objects.filter(visible=True)

    # 搜索的情况
    keyword = request.GET.get("keyword", "").strip()
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
        problems = tag.problem_set.all().filter(visible=True)

    paginator = Paginator(problems, 40)
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
    tags = ProblemTag.objects.annotate(problem_number=Count("problem")).filter(problem_number__gt=0).order_by(
        "-problem_number")

    return render(request, "oj/problem/problem_list.html",
                  {"problems": current_page, "page": int(page),
                   "previous_page": previous_page, "next_page": next_page,
                   "keyword": keyword, "tag": tag_text,
                   "tags": tags, "difficulty_order": difficulty_order})
