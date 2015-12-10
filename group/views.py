# coding=utf-8
from django.shortcuts import render
from django.db import IntegrityError

from rest_framework.views import APIView

from utils.shortcuts import error_response, serializer_invalid_response, success_response, paginate, error_page
from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN, User
from account.decorators import login_required

from .models import Group, JoinGroupRequest, UserGroupRelation, AdminGroupRelation
from .serializers import (CreateGroupSerializer, EditGroupSerializer,
                          CreateJoinGroupRequestSerializer, GroupSerializer,
                          GroupMemberSerializer, EditGroupMemberSerializer,
                          JoinGroupRequestSerializer, PutJoinGroupRequestSerializer, GroupPromoteAdminSerializer)
from announcement.models import Announcement
from django.core.paginator import Paginator
from django.db.models import Q


class GroupAPIViewBase(object):
    def get_group(self, request, group_id):
        """
        根据group_id查询指定的小组的信息，结合判断用户权限
        管理员可以查询所有的小组，其他用户查询自己创建的小组
        """
        if request.user.admin_type == SUPER_ADMIN:
            group = Group.objects.get(id=group_id)
        else:
            group = Group.objects.get(id=group_id, visible=True, admin=request.user)
        return group

    def get_groups(self, request):
        """
        如果是超级管理员，就返回全部的小组
        如果是管理员，就返回他创建的全部小组
        """
        if request.user.admin_type == SUPER_ADMIN:
            groups = Group.objects.filter()
        else:
            groups = Group.objects.filter(admin=request.user, visible=True)
        return groups


class GroupAdminAPIView(APIView, GroupAPIViewBase):
    def post(self, request):
        """
        创建小组的api
        ---
        request_serializer: CreateGroupSerializer
        response_serializer: GroupSerializer
        """
        serializer = CreateGroupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                group = Group.objects.create(name=data["name"],
                                             description=data["description"],
                                             join_group_setting=data["join_group_setting"],
                                             created_by=request.user)
            except IntegrityError:
                return error_response(u"小组名已经存在")
            AdminGroupRelation.objects.create(group=group, user=request.user)
            return success_response(GroupSerializer(group).data)
        else:
            return serializer_invalid_response(serializer)

    def put(self, request):
        """
        修改小组信息的api
        ---
        request_serializer: EditGroupSerializer
        response_serializer: GroupSerializer
        """
        serializer = EditGroupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                group = self.get_group(request, data["group_id"])
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
            try:
                group.name = data["name"]
                group.description = data["description"]
                group.join_group_setting = data["join_group_setting"]
                group.visible = data["visible"]
                group.save()
            except IntegrityError:
                return error_response(u"小组名已经存在")

            return success_response(GroupSerializer(group).data)
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        查询小组列表或者单个小组的信息，查询单个小组需要传递group_id参数，否则返回全部
        ---
        response_serializer: GroupSerializer
        """
        group_id = request.GET.get("group_id", None)
        # 根据 id 查询小组信息
        if group_id:
            try:
                group = self.get_group(request, group_id)
                return success_response(GroupSerializer(group).data)
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
        else:
            groups = self.get_groups(request)
            # 搜索小组
            if request.GET.get("keyword", None):
                groups = groups.filter(name__contains=request.GET["keyword"])
            # 只返回我创建的小组 适用于超级管理员
            if request.GET.get("my_group", None):
                groups = groups.filter(admin=request.user)
            # 只返回指定用户的小组 适用于管理员
            elif request.GET.get("admin_id", None):
                groups = groups.filter(admin__id=request.GET["admin_id"])
            return paginate(request, groups, GroupSerializer)


class GroupMemberAdminAPIView(APIView, GroupAPIViewBase):
    def get(self, request):
        """
        查询小组成员的api，需要传递group_id参数
        ---
        response_serializer: GroupMemberSerializer
        """
        group_id = request.GET.get("group_id", None)
        if not group_id:
            return error_response(u"参数错误")
        try:
            group = self.get_group(request, group_id)
        except Group.DoesNotExist:
            return error_response(u"小组不存在")
        admin_only = request.GET.get("admin_only", None)
        if admin_only:
            members = AdminGroupRelation.objects.filter(group=group)
        else:
            members = UserGroupRelation.objects.filter(group=group)
        
        return paginate(request, members, GroupMemberSerializer)

    def put(self, request):
        """
        删除小组成员的api接口
        ---
        request_serializer: EditGroupMemberSerializer
        """
        serializer = EditGroupMemberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                group = self.get_group(request, serializer.data["group_id"])
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
            user_id_list = serializer.data["members"]
            UserGroupRelation.objects.filter(group=group, user__id__in=user_id_list).delete()
            return success_response(u"删除成功")
        else:
            return serializer_invalid_response(serializer)


def join_group(user, group):
    try:
        UserGroupRelation.objects.create(user=user, group=group)
        return True
    except IntegrityError:
        return False


class JoinGroupAPIView(APIView):
    # @login_required
    def post(self, request):
        """
        加入某个小组的api
        ---
        request_serializer: CreateJoinGroupRequestSerializer
        """
        serializer = CreateJoinGroupRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                group = Group.objects.get(id=data["group_id"])
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
            if group.join_group_setting == 0:
                if join_group(request.user, group):
                    return success_response(u"你已经成功的加入该小组")
                else:
                    return error_response(u"你已经是小组成员了")
            elif group.join_group_setting == 1:
                if not data["message"]:
                    return error_response(u"message : 该字段是必填项。")
                try:
                    JoinGroupRequest.objects.get(user=request.user, group=group, status=False)
                    return error_response(u"你已经提交过申请了，请等待审核")
                except JoinGroupRequest.DoesNotExist:
                    JoinGroupRequest.objects.create(user=request.user, group=group, message=data["message"])
                return success_response(u"申请提交成功，请等待审核")
            elif group.join_group_setting == 2:
                return error_response(u"该小组不允许任何人加入")
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        搜索小组的api，需要传递keyword参数
        ---
        response_serializer: GroupSerializer
        """
        keyword = request.GET.get("keyword", None)
        if not keyword:
            return error_response(u"参数错误")
        # 搜索包含这个关键词的 没有解散的 而且允许加入的小组
        groups = Group.objects.filter(name__contains=keyword, visible=True, join_group_setting__lte=2)
        return paginate(request, groups, GroupSerializer)


class JoinGroupRequestAdminAPIView(APIView, GroupAPIViewBase):
    def get(self, request):
        """
        返回管理的群的加群请求
        ---
        response_serializer: JoinGroupRequestSerializer
        """
        requests = JoinGroupRequest.objects.filter(group__in=Group.objects.filter(admin=request.user, visible=True),
                                                   status=False)
        return paginate(request, requests, JoinGroupRequestSerializer)

    def put(self, request):
        """
        同意或者拒绝加入小组请求
        ---
        request_serializer: PutJoinGroupRequestSerializer
        """
        serializer = PutJoinGroupRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                join_request = JoinGroupRequest.objects.get(id=data["request_id"], group__admin=request.user,
                                                            status=False)
            except JoinGroupRequest.DoesNotExist:
                return error_response(u"请求不存在")

            join_request.status = True
            join_request.save()
            if data["status"]:
                if join_group(join_request.user, join_request.group):
                    join_request.accepted = True
                    join_request.save()
                    return success_response(u"加入成功")
                else:
                    return error_response(u"加入失败，已经在本小组内")
            else:
                return success_response(u"已拒绝")

        else:
            return serializer_invalid_response(serializer)


@login_required
def group_list_page(request, page=1):
    groups = Group.objects.filter(visible=True, join_group_setting__lte=2)
    # 搜索的情况
    keyword = request.GET.get("keyword", None)
    if keyword:
        groups = groups.filter(Q(name__contains=keyword) | Q(description__contains=keyword))

    paginator = Paginator(groups, 20)
    try:
        current_page = paginator.page(int(page))
    except Exception:
        return error_page(request, u"不存在的页码")

    previous_page = next_page = None

    try:
        previous_page = current_page.previous_page_number()
    except Exception:
        pass
    next_page = None
    try:
        next_page = current_page.next_page_number()
    except Exception:
        pass

    return render(request, "oj/group/group_list.html", {
        "groups": groups,
        "contests": current_page, "page": int(page),
        "previous_page": previous_page, "next_page": next_page,
        "keyword": keyword
    })


@login_required
def group_page(request, group_id):
    try:
        group = Group.objects.get(id=group_id, visible=True)
    except Group.DoesNotExist:
        return error_page(request, u"小组不存在")
    joined = True
    try:
        UserGroupRelation.objects.get(user=request.user, group=group)
    except UserGroupRelation.DoesNotExist:
        joined = False
    return render(request, "oj/group/group.html", {"group": group, "joined": joined})


@login_required
def application_list_page(request, group_id):
    try:
        group = Group.objects.get(id=group_id, visible=True)
    except Group.DoesNotExist:
        return error_page(request, u"小组不存在")
    applications = JoinGroupRequest.objects.filter(user=request.user, group=group)
    return render(request, "oj/group/my_application_list.html",
                  {"group": group, "applications": applications})


@login_required
def application_page(request, request_id):
    try:
        application = JoinGroupRequest.objects.get(user=request.user, pk=request_id)
    except JoinGroupRequest.DoesNotExist:
        return error_page(request, u"申请不存在")
    return render(request, "oj/group/my_application.html",
                  {"application": application})


class GroupPrometAdminAPIView(APIView):
    def post(self, request):
        """
        创建小组管理员的api
        ---
        request_serializer: GroupPromoteAdminSerializer
        """
        serializer = GroupPromoteAdminSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                group = Group.objects.get(id=data["group_id"])
            except Group.DoesNotExist:
                return error_response(u"小组不存在")
            try:
                user = User.objects.get(id=data["user_id"])
            except User.DoesNotExist:
                return error_response(u"用户不存在")
            try:
                AdminGroupRelation.objects.create(user=user, group=group)
            except IntegrityError:
                return error_response(u"该用户已经是管理员了")
            return success_response(u"操作成功")
        else:
            return serializer_invalid_response(serializer)
