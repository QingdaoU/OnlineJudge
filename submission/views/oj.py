from django.core.paginator import Paginator
from django_redis import get_redis_connection

from account.decorators import login_required
from account.models import AdminType, User
from problem.models import Problem
from submission.tasks import judge_task
# from judge.dispatcher import JudgeDispatcher
from utils.api import APIView, validate_serializer
from utils.shortcuts import build_query_string
from utils.throttling import TokenBucket, BucketController
from ..models import Submission, JudgeStatus
from ..serializers import CreateSubmissionSerializer, SubmissionModelSerializer


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
        problem = Problem.objects.get(id=problem_id)
    except Problem.DoesNotExist:
        return response.error("Problem not exist")

    submission = Submission.objects.create(user_id=user.id,
                                           language=language,
                                           code=code,
                                           problem_id=problem.id,
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
        if submission_id:
            try:
                submission = Submission.objects.get(id=submission_id, user_id=request.user.id)
            except Submission.DoesNotExist:
                return self.error("Submission not exist")
            return self.success(SubmissionModelSerializer(submission).data)

        problem_id = request.GET.get("problem_id")
        subs = Submission.objects.filter(contest_id__isnull=True)
        if problem_id:
            subs = subs.filter(problem_id=problem_id)

        if request.GET.get("myself"):
            subs = subs.filter(user_id=request.user.id)
        # todo: paginate
        return self.success(SubmissionModelSerializer(subs, many=True).data)


class SubmissionListAPI(APIView):
    """
    所有提交的列表
    """
    def get(self, request, **kwargs):
        submission_filter = {"my": None, "user_id": None}
        show_all = False
        page = kwargs.get("page", 1)

        user_id = request.GET.get("user_id")
        if user_id and request.user.admin_type == AdminType.SUPER_ADMIN:
            submission_filter["user_id"] = user_id
            submissions = Submission.objects.filter(user_id=user_id, contest_id__isnull=True)
        else:
            show_all = True
            if request.GET.get("my") == "true":
                submission_filter["my"] = "true"
                show_all = False
            if show_all:
                submissions = Submission.objects.filter(contest_id__isnull=True)
            else:
                submissions = Submission.objects.filter(user_id=request.user.id, contest_id__isnull=True)

        submissions = submissions.values("id", "user_id", "problem_id", "result", "created_time",
                                         "accepted_time", "language").order_by("-created_time")
        language = request.GET.get("language")
        if language:
            submissions = submissions.filter(language=language)
            submission_filter["language"] = language

        result = request.GET.get("result")
        if result:
            # TODO： 转换为数字结果
            submissions = submissions.filter(result=int(result))
            submission_filter["result"] = result

        paginator = Paginator(submissions, 20)
        try:
            submissions = paginator.page(int(page))
        except Exception:
            return self.error("Page not exist")

        # Cache
        cache_result = {"problem": {}, "user": {}}
        for item in submissions:
            problem_id = item["problem_id"]
            if problem_id not in cache_result["problem"]:
                problem = Problem.objects.get(id=problem_id)
                cache_result["problem"][problem_id] = problem.title
            item["title"] = cache_result["problem"][problem_id]

            user_id = item["user_id"]
            if user_id not in cache_result["user"]:
                user = User.objects.get(id=user_id)
                cache_result["user"][user_id] = user
            item["user"] = cache_result["user"][user_id]

            if item["user_id"] == request.user.id or request.user.admin_type == AdminType.SUPER_ADMIN:
                item["show_link"] = True
            else:
                item["show_link"] = False

        previous_page = next_page = None
        try:
            previous_page = submissions.previous_page_number()
        except Exception:
            pass
        try:
            next_page = submissions.next_page_number()
        except Exception:
            pass

        return self.success({"submissions": submissions.object_list, "page": int(page),
                             "previous_page": previous_page, "next_page": next_page,
                             "start_id": int(page) * 20 - 20,
                             "query": build_query_string(submission_filter),
                             "submission_filter": submission_filter,
                             "show_all": show_all})


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
        except (Problem.DoesNotExist, ):
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
