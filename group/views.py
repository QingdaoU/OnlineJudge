# coding=utf-8
from django.shortcuts import render

from rest_framework.views import APIView

from utils.shortcuts import error_response, serializer_invalid_response, success_response, paginate
from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN
from account.decorators import login_required

from .models import Group, JoinGroupRequest, UserGroupRelation
from .serializers import (CreateGroupSerializer, EditGroupSerializer,
                          JoinGroupRequestSerializer, GroupSerializer, 
                          GroupMemberSerializer, EditGroupMemberSerializer)


class GroupAPIViewBase(object):
    def get_group(request, group_id):
        """
        根据group_id查询指定的小组的信息，结合判断用户权限
        管理员可以查询所有的小组，其他用户查询自己创建的自傲组
        """
        if request.user.admin_type == SUPER_ADMIN:
            group = Group.object.get(id=group_id, visible=True)
        else:
            group = Group.object.get(id=group_id, visible=True, admin=request.user)
        return group
        
    def get_groups(request):
        """
        如果是超级管理员，就返回全部的小组
        如果是管理员，就返回他创建的全部小组
        """
        if request.user.admin_type == SUPER_ADMIN:
            groups = Group.objects.filter(visible=True)
        else:
            groups = Group.objects.filter(admin=request.user, visible=True)


class GroupAdminAPIView(APIView, GroupAPIViewBase):
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
                group = self.get_group(request, data["group_id"])
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
                group = self.get_group(request, group_id)
                return success_response(GroupSerializer(group).data)
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
        else:
            groups = self.get_groups(request)
            return paginate(request, groups, GroupSerializer)
            
            
class GroupMemberAdminAPIView(APIView, GroupAPIViewBase):
    def get(self, request):
        group_id = request.GET.get("group_id", None)
        if not group_id:
            return error_response(u"参数错误")
        try:
            group = self.get_group(request, group_id)
        except Group.DoesNotExist:
            return error_response(u"小组不存在")
        
        return paginate(request, UserGroupRelation.objects.filter(group=group), GroupMemberSerializer)
    
    def put(self, request):
        serializer = EditGroupMemberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                group = self.get_group(request, group_id)
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
            user_id_list = serializer.data["members"]
            UserGroupRelation.objects.delete(group=group, user__id__in=user_id_list)
            return success_response(u"删除成功")
        else:
            return serializer_invalid_response(serializer)


def join_group(user, group):
    return UserGroupRelation.objects.create(user=user, group=group)
            

class JoinGroupAPIView(APIView):
    @login_required
    def post(self, request):
        serializer = JoinGroupRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                group = Grouo.objects.get(id=data["group_id"])
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
        keyword = request.GET.get("keyword", None)
        if not keyword:
            return error_response(u"参数错误")
        # 搜索包含这个关键词的 没有解散的 而且允许加入的小组
        groups = Group.objects.filter(name__contains=keyword, visible=True, join_group_setting__lte=2)
        return paginate(request, groups, GroupSerializer)
