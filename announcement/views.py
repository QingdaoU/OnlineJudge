# coding=utf-8
from rest_framework.views import APIView

from utils.shortcuts import serializer_invalid_response, error_response, success_response

from account.models import User

from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementAPIView(APIView):
    # todo 判断用户是否需要登录
    def post(self, request):
        """
        公告发布json api接口
        ---
        request_serializer: AnnouncementSerializer
        """
        serializer = AnnouncementSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            Announcement.objects.create(title=data["title"],
                                        description=data["description"],
                                        created_by=request.user)
            return success_response(u"公告发布成功！")
        else:
            return serializer_invalid_response(serializer)