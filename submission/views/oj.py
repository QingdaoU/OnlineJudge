
from account.decorators import login_required, check_contest_permission
from judge.tasks import judge_task
from problem.models import Problem, ProblemRuleType, ContestProblem
from contest.models import Contest, ContestStatus
from utils.api import APIView, validate_serializer
from utils.throttling import TokenBucket, BucketController
from ..models import Submission
from ..serializers import CreateSubmissionSerializer, SubmissionModelSerializer
from ..serializers import SubmissionSafeSerializer, SubmissionListSerializer
from utils.cache import throttling_cache


# from judge.dispatcher import JudgeDispatcher


def _submit(response, user, problem_id, language, code, contest_id):
    # TODO: 预设默认值，需修改
    controller = BucketController(user_id=user.id,
                                  redis_conn=throttling_cache,
                                  default_capacity=30)
    bucket = TokenBucket(fill_rate=10, capacity=20,
                         last_capacity=controller.last_capacity,
                         last_timestamp=controller.last_timestamp)

    if bucket.consume():
        controller.last_capacity -= 1
    else:
        return response.error("Please wait %d seconds" % int(bucket.expected_time() + 1))
    try:
        if contest_id:
            problem = ContestProblem.objects.get(_id=problem_id, visible=True)
        else:
            problem = Problem.objects.get(_id=problem_id, visible=True)
    except Problem.DoesNotExist:
        return response.error("Problem not exist")

    submission = Submission.objects.create(user_id=user.id,
                                           language=language,
                                           code=code,
                                           problem_id=problem._id,
                                           contest_id=contest_id)
    # use this for debug
    # JudgeDispatcher(submission.id, problem._id).judge()
    judge_task.delay(submission.id, problem._id)
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
            if contest.status != ContestStatus.CONTEST_UNDERWAY and request.user != contest.created_by:
                return self.error("You have no permission to submit code.")
        return _submit(self, request.user, data["problem_id"], data["language"], data["code"], data.get("contest_id"))

    @login_required
    def get(self, request):
        submission_id = request.GET.get("id")
        if not submission_id:
            return self.error("Parameter id doesn't exist.")
        try:
            submission = Submission.objects.get(id=submission_id, user_id=request.user.id)
        except Submission.DoesNotExist:
            return self.error("Submission doesn't exist.")
        if not submission.check_user_permission(request.user):
            return self.error("No permission for this submission.")

        if submission.contest_id:
            # check problem'rule is ACM or IO.
            if ContestProblem.objects.filter(contest_id=submission.contest_id,
                                             _id=submission.problem_id,
                                             visible=True,
                                             rule_type=ProblemRuleType.ACM
                                             ).exists():
                return self.success(SubmissionSafeSerializer(submission).data)
            return self.success(SubmissionModelSerializer(submission).data)

        if Problem.objects.filter(_id=submission.problem_id,
                                  visible=True,
                                  rule_type=ProblemRuleType.ACM
                                  ).exists():
            return self.success(SubmissionSafeSerializer(submission).data)
        return self.success(SubmissionModelSerializer(submission).data)


class SubmissionListAPI(APIView):
    def get(self, request):
        if request.GET.get("contest_id"):
            return self._get_contest_submission_list(request)

        subs = Submission.objects.filter(contest_id__isnull=True)
        return self.process_submissions(request, subs)

    @check_contest_permission
    def _get_contest_submission_list(self, request):
        subs = Submission.objects.filter(contest_id=self.contest.id)
        return self.process_submissions(request, subs)

    def process_submissions(self, request, subs):
        problem_id = request.GET.get("problem_id")
        if problem_id:
            subs = subs.filter(problem_id=problem_id)

        if request.GET.get("myself") and request.GET["myself"] == "1":
            subs = subs.filter(user_id=request.user.id)
        data = self.paginate_data(request, subs)
        data["results"] = SubmissionListSerializer(data["results"], many=True, user=request.user).data
        return self.success(data)
