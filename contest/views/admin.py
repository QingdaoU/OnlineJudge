import dateutil.parser

from utils.api import APIView, validate_serializer

from ..models import Contest, ContestAnnouncement
from ..serializers import (ContestAnnouncementSerializer, ContestSerializer,
                           CreateConetestSeriaizer,
                           CreateContestAnnouncementSerializer,
                           EditConetestSeriaizer)


class ContestAPI(APIView):
    @validate_serializer(CreateConetestSeriaizer)
    def post(self, request):
        data = request.data
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        data["created_by"] = request.user
        if data["end_time"] <= data["start_time"]:
            return self.error("Start time must occur earlier than end time")
        if not data["password"]:
            data["password"] = None
        Contest.objects.create(**data)
        return self.success()

    @validate_serializer(EditConetestSeriaizer)
    def put(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data.pop("id"))
            if request.user.is_admin():
                contest = contest.get(created_by=request.user)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        if data["end_time"] <= data["start_time"]:
            return self.error("Start time must occur earlier than end time")
        if not data["password"]:
            data["password"] = None
        for k, v in data.items():
            setattr(contest, k, v)
        contest.save()
        return self.success(ContestSerializer(contest).data)

    def get(self, request):
        contest_id = request.GET.get("id")
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id)
                if request.user.is_admin():
                    contest = contest.get(created_by=request.user)
                return self.success(ContestSerializer(contest).data)
            except Contest.DoesNotExist:
                return self.error("Contest does not exist")

        contests = Contest.objects.all().order_by("-create_time")

        keyword = request.GET.get("keyword")
        if keyword:
            contests = contests.filter(title__contains=keyword)

        if request.user.is_admin():
            contests = contests.filter(created_by=request.user)
        return self.success(self.paginate_data(request, contests, ContestSerializer))


class ContestAnnouncementAPI(APIView):
    @validate_serializer(CreateContestAnnouncementSerializer)
    def post(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data.pop("contest_id"))
            if request.user.is_admin():
                contest = contest.get(created_by=request.user)
            data["contest"] = contest
            data["created_by"] = request.user
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        announcement = ContestAnnouncement.objects.create(**data)
        return self.success(ContestAnnouncementSerializer(announcement).data)

    def delete(self, request):
        announcement_id = request.GET.get("id")
        if announcement_id:
            if request.user.is_admin():
                ContestAnnouncement.objects.filter(id=announcement_id, contest__created_by=request.user).delete()
            else:
                ContestAnnouncement.objects.filter(id=announcement_id).delete()
        return self.success()
