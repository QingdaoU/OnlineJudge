# coding=utf-8
from rest_framework.views import APIView

from account.decorators import super_admin_required
from utils.shortcuts import success_response, serializer_invalid_response, error_response, paginate
from .serializers import CreateJudgesSerializer, JudgesSerializer, EditJudgesSerializer
from .models import JudgeServer


class AdminJudgeServerAPIView(APIView):
    @super_admin_required
    def post(self, request):
        """
        添加判题服务器 json api接口
        ---
        request_serializer: CreateJudgesSerializer
        response_serializer: JudgesSerializer
        """
        serializer = CreateJudgesSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            judge_server = JudgeServer.objects.create(name=data["name"], ip=data["ip"], port=data["port"],
                                                      max_instance_number=data["max_instance_number"],
                                                      token=data["token"])
            return success_response(JudgesSerializer(judge_server).data)
        else:
            return serializer_invalid_response(serializer)

    @super_admin_required
    def put(self, request):
        """
        修改判题服务器信息 json api接口
        ---
        request_serializer: EditJudgesSerializer
        response_serializer: JudgesSerializer
        """
        serializer = EditJudgesSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                judge_server = JudgeServer.objects.get(pk=data["id"])
            except JudgeServer.DoesNotExist:
                return error_response(u"此判题服务器不存在！")

            judge_server.name = data["name"]
            judge_server.ip = data["ip"]
            judge_server.port = data["port"]
            judge_server.max_instance_number = data["max_instance_number"]
            judge_server.token = data["token"]
            judge_server.status = data["status"]
            judge_server.save()
            return success_response(JudgesSerializer(judge_server).data)
        else:
            return serializer_invalid_response(serializer)

    @super_admin_required
    def get(self, request):
        """
        获取全部判题服务器
        """
        judge_server_id = request.GET.get("judge_server_id", None)
        if judge_server_id:
            try:
                judge_server = JudgeServer.objects.get(id=judge_server_id)
            except JudgeServer.DoesNotExist:
                return error_response(u"判题服务器不存在")
            return success_response(JudgesSerializer(judge_server).data)
        judge_server = JudgeServer.objects.all()

        return paginate(request, judge_server, JudgesSerializer)
