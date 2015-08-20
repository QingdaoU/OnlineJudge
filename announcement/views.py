# coding=utf-8
from rest_framework.views import APIView

from django.shortcuts import render
from utils.shortcuts import serializer_invalid_response, error_response, success_response

from utils.shortcuts import paginate, error_page
from account.models import SUPER_ADMIN, ADMIN
from group.models import Group
from .models import Announcement
from .serializers import (CreateAnnouncementSerializer, AnnouncementSerializer,
                          EditAnnouncementSerializer)


def announcement_page(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id, visible=True)
    except Announcement.DoesNotExist:
        return error_page(request, u"模板不存在")
    return render(request, "oj/announcement/announcement.html", {"announcement": announcement})


class AnnouncementAdminAPIView(APIView):
    def post(self, request):
        """
        公告发布json api接口
        ---
        request_serializer: CreateAnnouncementSerializer
        """
        serializer = CreateAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            groups = []
            # 如果不是全局公告，就去查询一下小组的id 列表中的内容，注意用户身份
            if not data["is_global"]:
                if request.user.admin_type == SUPER_ADMIN:
                    groups = Group.objects.filter(id__in=data["groups"])
                else:
                    groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                if not groups.count():
                    return error_response(u"至少选择一个小组")
            else:
                if request.user.admin_type != SUPER_ADMIN:
                    return error_response(u"只有超级管理员可以创建全局公告")

            announcement = Announcement.objects.create(title=data["title"],
                                                       content=data["content"],
                                                       created_by=request.user,
                                                       is_global=data["is_global"])

            announcement.groups.add(*groups)
            return success_response(u"公告发布成功！")
        else:
            return serializer_invalid_response(serializer)

    def put(self, request):
        """
        公告编辑json api接口
        ---
        request_serializer: EditAnnouncementSerializer
        response_serializer: AnnouncementSerializer
        """
        serializer = EditAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                if request.user.admin_type == SUPER_ADMIN:
                    announcement = Announcement.objects.get(id=data["id"])
                else:
                    announcement = Announcement.objects.get(id=data["id"], created_by=request.user)
            except Announcement.DoesNotExist:
                return error_response(u"公告不存在")
            groups = []
            if not data["is_global"]:
                if request.user.admin_type == SUPER_ADMIN:
                    groups = Group.objects.filter(id__in=data["groups"])
                else:
                    groups = Group.objects.filter(id__in=data["groups"], admin=request.user)
                if not groups.count():
                    return error_response(u"至少选择一个小组")
            announcement.title = data["title"]
            announcement.content = data["content"]
            announcement.visible = data["visible"]
            announcement.is_global = data["is_global"]
            announcement.save()

            # 重建小组和公告的对应关系
            announcement.groups.clear()
            announcement.groups.add(*groups)
            return success_response(AnnouncementSerializer(announcement).data)
        else:
            return serializer_invalid_response(serializer)

    def get(self, request):
        """
        公告分页json api接口
        ---
        response_serializer: AnnouncementSerializer
        """
        if request.user.admin_type == SUPER_ADMIN:
            announcement = Announcement.objects.all().order_by("-last_update_time")
        else:
            announcement = Announcement.objects.filter(created_by=request.user)
        visible = request.GET.get("visible", None)
        if visible:
            announcement = announcement.filter(visible=(visible == "true"))
        return paginate(request, announcement, AnnouncementSerializer)
