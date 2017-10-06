from account.decorators import login_required, check_contest_permission
from judge.tasks import judge_task
# from judge.dispatcher import JudgeDispatcher
from problem.models import Problem, ProblemRuleType
from contest.models import Contest, ContestStatus, ContestRuleType
from utils.api import APIView, validate_serializer
from utils.throttling import TokenBucket, BucketController
from utils.cache import cache
from ..models import Submission
from ..serializers import CreateSubmissionSerializer, SubmissionModelSerializer
from ..serializers import SubmissionSafeSerializer, SubmissionListSerializer


def _submit(response, user, problem_id, language, code, contest_id):
    # TODO: 预设默认值，需修改
    controller = BucketController(user_id=user.id,
                                  redis_conn=cache,
                                  default_capacity=30)
    bucket = TokenBucket(fill_rate=10, capacity=20,
                         last_capacity=controller.last_capacity,
                         last_timestamp=controller.last_timestamp)
    if bucket.consume():
        controller.last_capacity -= 1
    else:
        return response.error("Please wait %d seconds" % int(bucket.expected_time() + 1))

    try:
        problem = Problem.objects.get(id=problem_id,
                                      contest_id=contest_id,
                                      visible=True)
    except Problem.DoesNotExist:
        return response.error("Problem not exist")

    submission = Submission.objects.create(user_id=user.id,
                                           username=user.username,
                                           language=language,
                                           code=code,
                                           problem_id=problem.id,
                                           contest_id=contest_id)
    # use this for debug
    # JudgeDispatcher(submission.id, problem.id).judge()
    judge_task.delay(submission.id, problem.id)
    return response.success({"submission_id": submission.id})


class SubmissionAPI(APIView):
    @validate_serializer(CreateSubmissionSerializer)
    @login_required
    def post(self, request):
        data = request.data
        if data.get("contest_id"):
            try:
                contest = Contest.objects.get(id=data["contest_id"])
            except Contest.DoesNotExist:
                return self.error("Contest doesn't exist.")
            if contest.status == ContestStatus.CONTEST_ENDED:
                return self.error("The contest have ended")
            if contest.status == ContestStatus.CONTEST_NOT_START and request.user != contest.created_by:
                return self.error("Contest have not started")
        return _submit(self, request.user, data["problem_id"], data["language"], data["code"], data.get("contest_id"))

    @login_required
    def get(self, request):
        submission_id = request.GET.get("id")
        if not submission_id:
            return self.error("Parameter id doesn't exist.")
        try:
            submission = Submission.objects.select_related("problem").get(id=submission_id)
        except Submission.DoesNotExist:
            return self.error("Submission doesn't exist.")
        if not submission.check_user_permission(request.user):
            return self.error("No permission for this submission.")

        if submission.problem.rule_type == ProblemRuleType.ACM:
            return self.success(SubmissionSafeSerializer(submission).data)
        return self.success(SubmissionModelSerializer(submission).data)


class SubmissionListAPI(APIView):
    def get(self, request):
        if not request.GET.get("limit"):
            return self.error("Limit is needed")
        if request.GET.get("contest_id"):
            return self.error("Parameter error")

        submissions = Submission.objects.filter(contest_id__isnull=True)
        problem_id = request.GET.get("problem_id")
        myself = request.GET.get("myself")
        result = request.GET.get("result")
        if problem_id:
            try:
                problem = Problem.objects.get(_id=problem_id, contest_id__isnull=True, visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem doesn't exist")
            submissions = submissions.filter(problem=problem)
        if myself and myself == "1":
            submissions = submissions.filter(user_id=request.user.id)
        if result:
            submissions = submissions.filter(result=result)
        data = self.paginate_data(request, submissions)
        data["results"] = SubmissionListSerializer(data["results"], many=True, user=request.user).data
        return self.success(data)


class ContestSubmissionListAPI(APIView):
    @check_contest_permission
    def get(self, request):
        if not request.GET.get("limit"):
            return self.error("Limit is needed")

        contest = self.contest
        if contest.rule_type == ContestRuleType.OI and not contest.is_contest_admin(request.user):
            return self.error("No permission for OI contest submissions")

        submissions = Submission.objects.filter(contest_id=contest.id)
        problem_id = request.GET.get("problem_id")
        myself = request.GET.get("myself")
        result = request.GET.get("result")
        if problem_id:
            try:
                problem = Problem.objects.get(_id=problem_id, contest_id=contest.id, visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem doesn't exist")
            submissions = submissions.filter(problem=problem)

        if myself and myself == "1":
            submissions = submissions.filter(user_id=request.user.id)
        if result:
            submissions = submissions.filter(result=result)

        # filter the test submissions submitted before contest start
        if contest.status != ContestStatus.CONTEST_NOT_START:
            submissions = submissions.filter(create_time__gte=contest.start_time)

        # 封榜的时候只能看到自己的提交
        if not contest.real_time_rank and not contest.is_contest_admin(request.user):
            submissions = submissions.filter(user_id=request.user.id)

        data = self.paginate_data(request, submissions)
        data["results"] = SubmissionListSerializer(data["results"], many=True, user=request.user).data
        return self.success(data)
