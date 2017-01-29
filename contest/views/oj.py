from utils.api import APIView

from ..models import ContestAnnouncement
from ..serializers import ContestAnnouncementSerializer


class ContestAnnouncementListAPI(APIView):
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Invalid parameter")
        data = ContestAnnouncement.objects.filter(contest_id=contest_id).order_by("-create_time")
        max_id = request.GET.get("max_id")
        if max_id:
            data = data.filter(id__gt=max_id)
        return self.success(ContestAnnouncementSerializer(data, many=True).data)
