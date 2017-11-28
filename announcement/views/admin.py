from account.decorators import super_admin_required
from utils.api import APIView, validate_serializer

from announcement.models import Announcement
from announcement.serializers import (AnnouncementSerializer, CreateAnnouncementSerializer,
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
                                                   created_by=request.user,
                                                   visible=data["visible"])
        return self.success(AnnouncementSerializer(announcement).data)

    @validate_serializer(EditAnnouncementSerializer)
    @super_admin_required
    def put(self, request):
        """
        edit announcement
        """
        data = request.data
        try:
            announcement = Announcement.objects.get(id=data.pop("id"))
        except Announcement.DoesNotExist:
            return self.error("Announcement does not exist")

        for k, v in data.items():
            setattr(announcement, k, v)
        announcement.save()

        return self.success(AnnouncementSerializer(announcement).data)

    @super_admin_required
    def get(self, request):
        """
        get announcement list / get one announcement
        """
        announcement_id = request.GET.get("id")
        if announcement_id:
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                return self.success(AnnouncementSerializer(announcement).data)
            except Announcement.DoesNotExist:
                return self.error("Announcement does not exist")
        announcement = Announcement.objects.all().order_by("-create_time")
        if request.GET.get("visible") == "true":
            announcement = announcement.filter(visible=True)
        return self.success(self.paginate_data(request, announcement, AnnouncementSerializer))

    @super_admin_required
    def delete(self, request):
        if request.GET.get("id"):
            Announcement.objects.filter(id=request.GET["id"]).delete()
        return self.success()
