from utils.api import APIView

from announcement.models import Announcement, AboutUs
from announcement.serializers import AnnouncementSerializer, AboutUsSerializer


class AnnouncementAPI(APIView):
    def get(self, request):
        announcements = Announcement.objects.filter(visible=True)
        return self.success(self.paginate_data(request, announcements, AnnouncementSerializer))


class AboutUsAPI(APIView):
    def get(self, request):
        try:
            aboutus = AboutUs.objects.get(id=1)
            return self.success(AboutUsSerializer(aboutus).data)
        except AboutUs.DoesNotExist:
            return self.error("About Us does not exist")
