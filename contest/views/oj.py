import pickle
from django.utils.timezone import now
from django.db.models import Q
from utils.api import APIView, validate_serializer
from utils.cache import default_cache
from utils.constants import CacheKey
from account.decorators import login_required, check_contest_permission

from ..models import ContestAnnouncement, Contest, ContestStatus, ContestRuleType
from ..models import OIContestRank, ACMContestRank
from ..serializers import ContestAnnouncementSerializer
from ..serializers import ContestSerializer, ContestPasswordVerifySerializer
from ..serializers import OIContestRankSerializer, ACMContestRankSerializer


class ContestAnnouncementListAPI(APIView):
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Invalid parameter")
        data = ContestAnnouncement.objects.select_related("created_by").filter(contest_id=contest_id)
        max_id = request.GET.get("max_id")
        if max_id:
            data = data.filter(id__gt=max_id)
        return self.success(ContestAnnouncementSerializer(data, many=True).data)


class ContestAPI(APIView):
    def get(self, request):
        contest_id = request.GET.get("id")
        if contest_id:
            try:
                contest = Contest.objects.select_related("created_by").get(id=contest_id, visible=True)
            except Contest.DoesNotExist:
                return self.error("Contest doesn't exist.")
            return self.success(ContestSerializer(contest).data)

        contests = Contest.objects.select_related("created_by").filter(visible=True)
        keyword = request.GET.get("keyword")
        rule_type = request.GET.get("rule_type")
        status = request.GET.get("status")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        if rule_type:
            contests = contests.filter(rule_type=rule_type)
        if status:
            cur = now()
            if status == ContestStatus.CONTEST_NOT_START:
                contests = contests.filter(start_time__gt=cur)
            elif status == ContestStatus.CONTEST_ENDED:
                contests = contests.filter(end_time__lt=cur)
            else:
                contests = contests.filter(Q(start_time__lte=cur) & Q(end_time__gte=cur))
        return self.success(self.paginate_data(request, contests, ContestSerializer))


class ContestPasswordVerifyAPI(APIView):
    @validate_serializer(ContestPasswordVerifySerializer)
    @login_required
    def post(self, request):
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


class ContestAccessAPI(APIView):
    @login_required
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Parameter contest_id not exist.")
        if "contests" not in request.session:
            request.session["contests"] = []
        if int(contest_id) in request.session["contests"]:
            return self.success({"Access": True})
        else:
            return self.success({"Access": False})


class ContestRankAPI(APIView):
    def get_rank(self):
        if self.contest.rule_type == ContestRuleType.ACM:
            return ACMContestRank.objects.filter(contest=self.contest). \
                select_related("user").order_by("-accepted_number", "total_time")
        else:
            return OIContestRank.objects.filter(contest=self.contest). \
                select_related("user").order_by("-total_score")

    @check_contest_permission
    def get(self, request):
        if self.contest.rule_type == ContestRuleType.ACM:
            serializer = ACMContestRankSerializer
        else:
            serializer = OIContestRankSerializer

        cache_key = CacheKey.contest_rank_cache + str(self.contest.id)
        qs = default_cache.get(cache_key)
        if not qs:
            ranks = self.get_rank()
            default_cache.set(cache_key, pickle.dumps(ranks))
        else:
            ranks = pickle.loads(qs)

        return self.success(self.paginate_data(request, ranks, serializer))
