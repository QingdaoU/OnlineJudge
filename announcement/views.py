from django.utils.translation import ugettext as _

from account.decorators import super_admin_required
from utils.api import APIView, validate_serializer, IDOnlySerializer

from .models import Announcement
from .serializers import (CreateAnnouncementSerializer, AnnouncementSerializer,
                          EditAnnouncementSerializer)


class AnnouncementAdminAPI(APIView):
    @validate_serializer(CreateAnnouncementSerializer)
    @super_admin_required
    def post(self, request):
        """
        publish announcement
        """
        data = request.data
        announcement = Announcement.objects.create(title=data["title"],
                                                   content=data["content"],
                                                   created_by=request.user)
        return self.success(AnnouncementSerializer(announcement).data)

    @validate_serializer(EditAnnouncementSerializer)
    @super_admin_required
    def put(self, request):
        """
        edit announcement
        """
        data = request.data
        try:
            announcement = Announcement.objects.get(id=data["id"])
        except Announcement.DoesNotExist:
            return self.error(_("Announcement does not exist"))

        announcement.title = data["title"]
        announcement.content = data["content"]
        announcement.visible = data["visible"]
        announcement.save()

        return self.success(AnnouncementSerializer(announcement).data)

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

    @validate_serializer(IDOnlySerializer)
    @super_admin_required
    def delete(self, request):
        Announcement.objects.filter(id=request.data["id"]).delete()
        return self.success()
