from utils.api import APIView, validate_serializer
from account.decorators import login_required

from ..models import ContestAnnouncement, Contest
from ..serializers import ContestAnnouncementSerializer
from ..serializers import ContestSerializer, ContestPasswordVerifySerializer


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


class ContestAPI(APIView):
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id, visible=True)
                return self.success(ContestSerializer(contest).data)
            except Contest.DoesNotExist:
                return self.error("Contest doesn't exist.")

        contests = Contest.objects.filter(visible=True)
        keyword = request.GET.get("keyword")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        return self.success(self.paginate_data(request, contests, ContestSerializer))


class ContestPasswordVerifyAPI(APIView):
    @validate_serializer(ContestPasswordVerifySerializer)
    @login_required
    def get(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data["contest_id"], visible=True, password__isnull=False)
        except Contest.DoesNotExist:
            return self.error("Contest %s doesn't exist." % data["contest_id"])
        if contest.password != data["password"]:
            return self.error("Password doesn't match.")

        # password verify OK.
        if "contests" not in request.session:
            request.session["contests"] = []
        request.session["contests"].append(int(data["contest_id"]))
        # https://docs.djangoproject.com/en/dev/topics/http/sessions/#when-sessions-are-saved
        request.session.modified = True
        return self.success(True)
