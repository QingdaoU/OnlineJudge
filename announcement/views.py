# coding=utf-8
from rest_framework.views import APIView

from utils.shortcuts import serializer_invalid_response, error_response, success_response

from account.models import User
from utils.shortcuts import paginate
from .models import Announcement
from .serializers import CreateAnnouncementSerializer, AnnouncementSerializer


class AnnouncementAdminAPIView(APIView):
    def post(self, request):
        """
        公告发布json api接口
        ---
        request_serializer: CreateAnnouncementSerializer
        """
        serializer = CreateAnnouncementSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            Announcement.objects.create(title=data["title"],
                                        content=data["content"],
                                        created_by=request.user)
            return success_response(u"公告发布成功！")
        else:
            return serializer_invalid_response(serializer)


class AnnouncementAPIView(APIView):
    def get(self, request):
        """
        公告分页json api接口
        ---
        request_serializer: AnnouncementSerializer
        """
        announcement = Announcement.objects.all().order_by("last_update_time")
        return paginate(request, announcement, AnnouncementSerializer)
