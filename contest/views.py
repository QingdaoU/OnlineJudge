# coding=utf-8
import json
from django.shortcuts import render
from django.db import IntegrityError
from django.db.models import Q
from rest_framework.views import APIView
from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, paginate, rand_str, error_page)

from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN
from group.models import Group

from .models import Contest, ContestProblem
from .serializers import (CreateContestSerializer, ContestSerializer, EditContestSerializer,
                          CreateContestProblemSerializer, ContestProblemSerializer, EditContestProblemSerializer)



def contest_page(request, contest_id):
    pass


class ContestAdminAPIView(APIView):
    def post(self, request):
        """
        比赛发布json api接口
        ---
        request_serializer: CreateContestSerializer
        response_serializer: ContestSerializer
        """
        serializer = CreateContestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            groups = []
            # 首先判断比赛的类型： 0 即为是小组赛，1 即为是无密码的公开赛，2 即为是有密码的公开赛
                # 密码字段不为空的情况，此时为有密码的公开赛，
            # 此时为有密码的公开赛，并且此时只能超级管理员才有权限此创建比赛
            if data["contest_type"] == 2:
                if data["password"]:
                    if request.user.admin_type == SUPER_ADMIN:
                        pass
                    else:
                        return error_response(u"只有超级管理员才可创建公开赛（有密码）")
                else:
                    return error_response(u"此比赛为有密码的公开赛，密码不可为空")
            # 此时为没有密码的公开赛，并且此时只能是超级管理员才有权限创建此比赛
            elif data["contest_type"]:
                if not data["password"]:
                    if request.user.admin_type == SUPER_ADMIN:
                        pass
                    else:
                        return error_response(u"只有超级管理员才可创建公开赛（没有密码）")
                else:
                    return error_response(u"此比赛为没有密码的公开赛，密码无需填写")
            # 此时为没有密码的小组赛，并且此时只能是超级管理员和管理员才有权限创建此比赛
            else:
                if request.user.admin_type == REGULAR_USER:
                    return error_response(u"只有超级管理员和管理员才有权限创建比赛")
                else:
                    if not data["password"]:
                        groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                    else:
                        return error_response(u"此比赛为没有密码的小组赛，密码无需填写")
            try:
                contest = Contest.objects.create(title=data["title"], description=data["description"],
                                                 mode=data["mode"], show_rank=data["show_rank"],
                                                 show_user_submission=data["show_user_submission"],
                                                 start_time=["start_time"], end_time=data["end_time"])
                if data["password"]:
                    contest.setpassword(data["password"])
                contest.save()
            except IntegrityError:
                return error_response(u"比赛名已经存在")
            contest.groups.add(*groups)
            return success_response(ContestSerializer(contest).data)
        else:
            serializer_invalid_response(serializer)

    def put(self, request):
        """
        比赛编辑json api接口
        ---
        request_serializer: EditContestSerializer
        response_serializer: ContestSerializer
        """
        serializer = EditContestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                contest = Contest.objects.get(id=data["id"])
            except Contest.DoesNotExist:
                error_response(u"该比赛不存在！")
            try:
                contest.title = data["contest"]
                contest.description = data["description"]
                contest.mode = data["mode"]
                contest.show_rank = data["show_"]
                if data["password"]:
                    contest.set_password(data["password"])
                contest.save()
            except IntegrityError:
                return error_response(u"比赛名已经存在")

            return success_response(ContestSerializer(contest).data)
        else:
            serializer_invalid_response(serializer)

    def get(self, request):
        """
        比赛分页json api接口
        ---
        response_serializer: ContestSerializer
        """
        contest = Contest.objects.all().order_by("-last_updated_time")
        visible = request.GET.get("visible", None)
        if visible:
            contest = contest.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            contest = contest.filter(Q(title__contains=keyword) |
                                     Q(description__contains=keyword))
        return paginate(request, contest, ContestSerializer)


class ContestProblemAdminAPIView(APIView):
    def post(self, request):
        """
        比赛题目发布json api接口
        ---
        request_serializer: CreateContestProblemSerializer
        response_serializer: ContestProblemSerializer
        """
        serializer = CreateContestProblemSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            contest_problem = ContestProblem.objects.create(title=data["title"],
                                                            description=data["description"],
                                                            input_description=data["input_description"],
                                                            output_description=data["output_description"],
                                                            test_case_id=data["test_case_id"],
                                                            samples=json.dumps(data["samples"]),
                                                            time_limit=data["time_limit"],
                                                            memory_limit=data["memory_limit"],
                                                            difficulty=data["difficulty"],
                                                            created_by=request.user,
                                                            hint=data["hint"],
                                                            contest=request.contest,
                                                            sort_index=data["sort_index"])
            return success_response(ContestProblemSerializer(contest_problem).data)
        else:
            serializer_invalid_response(serializer)

    def put(self, request):
        """
        比赛题目编辑json api接口
        ---
        request_serializer: EditContestSerializer
        response_serializer: ContestProblemSerializer
        """
        serializer = EditContestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                contest_problem = ContestProblem.objects.get(id=data["id"])
            except ContestProblem.DoesNotExist:
                return error_response(u"该比赛题目不存在！")
            contest_problem.title = data["title"]
            contest_problem.description = data["description"]
            contest_problem.input_description = data["input_description"]
            contest_problem.output_description = data["output_description"]
            contest_problem.test_case_id = data["test_case_id"]
            contest_problem.time_limit = data["time_limit"]
            contest_problem.memory_limit = data["memory_limit"]
            contest_problem.difficulty = data["difficulty"]
            contest_problem.samples = json.dumps(data["samples"])
            contest_problem.hint = data["hint"]
            contest_problem.visible = data["visible"]
            contest_problem.sort_index = data["sort_index"]
            contest_problem.save()
            return success_response(ContestProblem(contest_problem).data)
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        比赛题目分页json api接口
        ---
        response_serializer: ProblemSerializer
        """
        contest_problem_id = request.GET.get("contest_problem_id", None)
        if contest_problem_id:
            try:
                contest_problem = ContestProblemSerializer.objects.get(id=contest_problem_id)
                return success_response(ContestProblemSerializer(contest_problem).data)
            except contest_problem.DoesNotExist:
                return error_response(u"比赛题目不存在")
        contest_problem = ContestProblem.objects.all().order_by("sort_index")
        visible = request.GET.get("visible", None)
        if visible:
            contest_problem = contest_problem.filter(visible=(visible == "true"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            contest_problem = contest_problem.filter(Q(title__contains=keyword) |
                                                     Q(description__contains=keyword))

        return paginate(request, contest_problem, ContestProblemSerializer)