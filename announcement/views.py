# coding=utf-8
from rest_framework.views import APIView

from django.shortcuts import render
from utils.shortcuts import serializer_invalid_response, error_response, success_response

from utils.shortcuts import paginate, error_page
from account.models import SUPER_ADMIN, ADMIN
from account.decorators import super_admin_required
from group.models import Group
from .models import Announcement
from .serializers import (CreateAnnouncementSerializer, AnnouncementSerializer,
                          EditAnnouncementSerializer)


def announcement_page(request, announcement_id):
    """
    公告的详情页面
    """
    try:
        announcement = Announcement.objects.get(id=announcement_id, visible=True)
    except Announcement.DoesNotExist:
        return error_page(request, u"公告不存在")
    return render(request, "oj/announcement/announcement.html", {"announcement": announcement})


class AnnouncementAdminAPIView(APIView):
    @super_admin_required
    def post(self, request):
        """
        公告发布json api接口
        ---
        request_serializer: CreateAnnouncementSerializer
        """
        serializer = CreateAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            Announcement.objects.create(title=data["title"], content=data["content"], created_by=request.user)
            return success_response(u"公告发布成功！")
        else:
            return serializer_invalid_response(serializer)

    @super_admin_required
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
                announcement = Announcement.objects.get(id=data["id"])
            except Announcement.DoesNotExist:
                return error_response(u"公告不存在")

            announcement.title = data["title"]
            announcement.content = data["content"]
            announcement.visible = data["visible"]
            announcement.save()

            return success_response(AnnouncementSerializer(announcement).data)
        else:
            return serializer_invalid_response(serializer)

    @super_admin_required
    def get(self, request):
        """
        公告分页json api接口
        ---
        response_serializer: AnnouncementSerializer
        """
        announcement = Announcement.objects.all().order_by("-create_time")
        visible = request.GET.get("visible", None)
        if visible:
            announcement = announcement.filter(visible=(visible == "true"))
        return paginate(request, announcement, AnnouncementSerializer)
