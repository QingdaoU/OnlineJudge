from django.utils.translation import ugettext as _

from account.decorators import super_admin_required
from utils.api import APIView

from .models import Announcement
from .serializers import (CreateAnnouncementSerializer, AnnouncementSerializer,
                          EditAnnouncementSerializer)


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
            return self.success(AnnouncementSerializer(announcement).data)
        else:
            return self.invalid_serializer(serializer)

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
                return self.error(_("Announcement does not exist"))

            announcement.title = data["title"]
            announcement.content = data["content"]
            announcement.visible = data["visible"]
            announcement.save()

            return self.success(AnnouncementSerializer(announcement).data)
        else:
            return self.invalid_serializer(serializer)

    @super_admin_required
    def get(self, request):
        """
        get announcement list / get one announcement
        """
        announcement_id = request.GET.get("announcement_id")
        if announcement_id:
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                return self.success(AnnouncementSerializer(announcement).data)
            except Announcement.DoesNotExist:
                return self.error(_("Announcement does not exist"))
        announcement = Announcement.objects.all().order_by("-create_time")
        if request.GET.get("visible") == "true":
            announcement = announcement.filter(visible=True)
        return self.success(self.paginate_data(request, announcement, AnnouncementSerializer))
