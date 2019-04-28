from utils.api import APIView

from announcement.models import (Announcement, AboutUs)
from announcement.serializers import (AnnouncementSerializer, AboutUsSerializer)


class AnnouncementAPI(APIView):
    def get(self, request):
        announcements = Announcement.objects.filter(visible=True)
        return self.success(self.paginate_data(request, announcements, AnnouncementSerializer))

class AboutUsAPI(APIView):
    def get(self, request):
        aboutus = AboutUs.objects.filter()
        return self.success(self.paginate_data(request, aboutus, AboutUsSerializer))