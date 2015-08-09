# coding=utf-8
from django.shortcuts import render

from rest_framework.views import APIView

from utils.shortcuts import error_response, serializer_invalid_response, success_response, paginate
from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN
from account.decorators import login_required

from .models import Group, JoinGroupRequest, UserGroupRelation
from .serializers import (CreateGroupSerializer, EditGroupSerializer,
                          JoinGroupRequestSerializer, GroupSerializer)


class GroupAdminAPIView(APIView):
    def post(self, request):
        """
        创建小组的api
        ---
        request_serializer: CreateGroupSerializer
        """
        serializer = CreateGroupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            group = Group.objects.create(name=data["name"],
                                         description=data["description"],
                                         join_group_setting=data["join_group_setting"],
                                         admin=request.user)
            return success_response(GroupSerializer(group).data)
        else:
            return serializer_invalid_response(serializer)

    def put(self, request):
        """
        修改小组信息的api
        ---
        request_serializer: EditGroupSerializer
        """
        serializer = EditGroupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                group = Group.objects.get(id=data["id"], admin=request.user)
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
            group.name = data["name"]
            group.description = data["description"]
            group.join_group_setting = data["join_group_setting"]
            group.save()
            return success_response(GroupSerializer(group).data)
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        查询小组列表或者单个小组的信息
        ---
        response_serializer: GroupSerializer
        """
        group_id = request.GET.get("group_id", None)
        if group_id:
            try:
                if request.user.admin_type == SUPER_ADMIN:
                    group = Group.object.get(id=group_id)
                else:
                    group = Group.object.get(id=group_id, admin=request.user)
                return success_response(GroupSerializer(group).data)
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
        else:
            if request.user.admin_type == SUPER_ADMIN:
                groups = Group.objects.filter(visible=True)
            else:
                groups = Group.objects.filter(admin=request.user, visible=True)
            return paginate(request, groups, GroupSerializer)
            
            
def join_group(user, group):
    return UserGroupRelation.objects.create(user=user, group=group)
            

class JoinGroupAPIView(APIView):
    @login_required
    def post(self, request):
        serializer = JoinGroupRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                group = Grouo.objects.get(id=data["group"])
            except Group.DesoNotExist:
                return error_response(u"小组不存在")
            if group.join_group_setting == 0:
                join_group(request.user, group)
                return success_response(u"你已经成功的加入该小组")
            elif group.join_group_setting == 1:
                return success_response(u"申请提交成功，请等待审核")
            elif group.join_group_setting == 2:
                return error_response(u"该小组不允许任何人加入")
        else:
            return serializer_invalid_response(serializer)
    
    def get(self, request):
        pass