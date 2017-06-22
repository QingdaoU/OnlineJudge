from utils.api import APIView

from ..models import ContestAnnouncement, Contest
from ..serializers import ContestAnnouncementSerializer
from ..serializers import ContestSerializer


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


class ContestListAPI(APIView):
    def get(self, request):
        contest_id = request.GET.get("id")
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id, visible=True)
                return self.success(ContestSerializer(contest).data)
            except Contest.DoesNotExist:
                return self.error("Contest Doesn't exist.")

        contests = Contest.objects.filter(visible=True)
        keyword = request.GET.get("keyword")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        return self.success(self.paginate_data(request, contests, ContestSerializer))
