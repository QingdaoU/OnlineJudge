from django_redis import get_redis_connection

from account.decorators import login_required
from account.models import AdminType, User
from problem.models import Problem, ProblemRuleType
from submission.tasks import judge_task
# from judge.dispatcher import JudgeDispatcher
from utils.api import APIView, validate_serializer
from utils.throttling import TokenBucket, BucketController
from ..models import Submission, JudgeStatus
from ..serializers import CreateSubmissionSerializer, SubmissionModelSerializer
from ..serializers import SubmissionSafeSerializer, SubmissionListSerializer



def _submit(response, user, problem_id, language, code, contest_id=None):
    # TODO: 预设默认值，需修改
    controller = BucketController(user_id=user.id,
                                  redis_conn=get_redis_connection("Throttling"),
                                  default_capacity=30)
    bucket = TokenBucket(fill_rate=10, capacity=20,
                         last_capacity=controller.last_capacity,
                         last_timestamp=controller.last_timestamp)

    if bucket.consume():
        controller.last_capacity -= 1
    else:
        return response.error("Please wait %d seconds" % int(bucket.expected_time() + 1))

    try:
        problem = Problem.objects.get(_id=problem_id)
    except Problem.DoesNotExist:
        return response.error("Problem not exist")

    submission = Submission.objects.create(user_id=user.id,
                                           language=language,
                                           code=code,
                                           problem_id=problem._id,
                                           contest_id=contest_id)
    # todo 暂时保留 方便排错
    # JudgeDispatcher(submission.id, problem.id).judge()
    judge_task.delay(submission.id, problem.id)
    return response.success({"submission_id": submission.id})


class SubmissionAPI(APIView):
    @validate_serializer(CreateSubmissionSerializer)
    @login_required
    def post(self, request):
        data = request.data
        return _submit(self, request.user, data["problem_id"], data["language"], data["code"])

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

        # check problem'rule is ACM or IO.
        if Problem.objects.filter(_id=submission.problem_id,
                                  visible=True,
                                  rule_type=ProblemRuleType.ACM
                                  ).exists():
            return self.success(SubmissionSafeSerializer(submission).data)
        return self.success(SubmissionModelSerializer(submission).data)


class SubmissionListAPI(APIView):
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if contest_id:
            subs = Submission.objects.filter(contest_id=contest_id)
        else:
            subs = Submission.objects.filter(contest_id__isnull=True)

        problem_id = request.GET.get("problem_id")
        if problem_id:
            subs = subs.filter(problem_id=problem_id)

        if request.GET.get("myself"):
            subs = subs.filter(user_id=request.user.id)
        # todo: paginate
        return self.success(SubmissionListSerializer(subs, many=True, user=request.user).data)


def _get_submission(submission_id, user):
    """
    用户权限判断
    """
    submission = Submission.objects.get(id=submission_id)
    # Super Admin / Owner / Share
    if user.admin_type == AdminType.SUPER_ADMIN or submission.user_id == user.id:
        return {"submission": submission, "can_share": True}
    if submission.contest_id:
        # 比赛部分
        pass
    if submission.shared:
        return {"submission": submission, "can_share": False}
    else:
        raise Submission.DoesNotExist


class SubmissionDetailAPI(APIView):
    """
    单个提交页面详情
    """

    def get(self, request, **kwargs):
        try:
            result = _get_submission(kwargs["submission_id"], request.user)
            submission = result["submission"]
        except Submission.DoesNotExist:
            return self.error("Submission not exist")

        # TODO: Contest
        try:
            if submission.contest_id:
                # problem = ContestProblem.objects.get(id=submission.problem_id, visible=True)
                pass
            else:
                problem = Problem.objects.get(id=submission.problem_id, visible=True)
        except (Problem.DoesNotExist,):
            return self.error("Submission not exist")

        if submission.result in [JudgeStatus.COMPILE_ERROR, JudgeStatus.SYSTEM_ERROR, JudgeStatus.PENDING]:
            info = submission.info
        else:
            info = submission.info
            if "test_case" in info[0]:
                info = sorted(info, key=lambda x: x["test_case"])

        user = User.objects.get(id=submission.user_id)
        return self.success({"submission": submission, "problem": problem, "info": info,
                             "user": user, "can_share": result["can_share"]})
