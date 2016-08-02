# coding=utf-8
from __future__ import unicode_literals
from rest_framework.views import APIView

from django.shortcuts import render
from django.utils.translation import ugettext as _
from utils.shortcuts import serializer_invalid_response, error_response, success_response

from utils.shortcuts import paginate, error_page
from account.decorators import super_admin_required
from .models import Announcement
from .serializers import (CreateAnnouncementSerializer, AnnouncementSerializer,
                          EditAnnouncementSerializer)


def announcement_page(request, announcement_id):
    """
    announcement detail page
    """
    try:
        announcement = Announcement.objects.get(id=announcement_id, visible=True)
    except Announcement.DoesNotExist:
        return error_page(request, _("Announcement does not exist"))
    return render(request, "oj/announcement/announcement.html", {"announcement": announcement})


class AnnouncementAdminAPIView(APIView):
    @super_admin_required
    def post(self, request):
        """
        publish announcement
        """
        serializer = CreateAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            announcement = Announcement.objects.create(title=data["title"],
                                                       content=data["content"],
                                                       created_by=request.user)
            return success_response(AnnouncementSerializer(announcement).data)
        else:
            return serializer_invalid_response(serializer)

    @super_admin_required
    def put(self, request):
        """
        edit announcement
        """
        serializer = EditAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                announcement = Announcement.objects.get(id=data["id"])
            except Announcement.DoesNotExist:
                return error_response(_("Announcement does not exist"))

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
        get announcement list / get one announcement
        """
        announcement_id = request.GET.get("announcement_id")
        if announcement_id:
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                return success_response(AnnouncementSerializer(announcement).data)
            except Announcement.DoesNotExist:
                return error_response(_("Announcement does not exist"))
        announcement = Announcement.objects.all().order_by("-create_time")
        return paginate(request, announcement, AnnouncementSerializer)
