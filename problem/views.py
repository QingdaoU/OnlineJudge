# coding=utf-8
import zipfile
import re
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView

from utils.shortcuts import rand_str, error_response, success_response


def problem_page(request, problem_id):
    # todo
    return render(request, "oj/problem/problem.html")


class TestCaseUploadAPIView(APIView):

    def _is_legal_test_case_file_name(self, file_name):
        # 正整数开头的 .in 或者.out 结尾的
        regex = r"^[1-9]\d*\.(in|out)$"
        return re.compile(regex).match(file_name) is not None

    @csrf_exempt
    def post(self, request):
        f = request.FILES["file"]

        tmp_zip = "tmp/" + rand_str() + ".zip"
        with open(tmp_zip) as test_case_zip:
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
                    name = file_name.spit(".")
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
            for name in l:
                f = open(test_case_dir + name, "w+b")
                f.write(test_case_file.read(name))
                f.close()

            return success_response(problem_test_dir)

        else:
            return error_response(u"测试用例压缩文件格式错误，请保证测试用例文件在根目录下直接压缩")

