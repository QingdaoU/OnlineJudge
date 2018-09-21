import ipaddress

from account.decorators import login_required, check_contest_permission
from judge.tasks import judge_task
from judge.dispatcher import Foo
# from judge.dispatcher import JudgeDispatcher
from problem.models import Problem, ProblemRuleType
from contest.models import Contest, ContestStatus, ContestRuleType
from options.options import SysOptions
from utils.api import APIView, validate_serializer
from utils.throttling import TokenBucket
from utils.captcha import Captcha
from utils.cache import cache
from ..models import Submission
from ..serializers import (CreateSubmissionSerializer, SubmissionModelSerializer,
                           ShareSubmissionSerializer)
from ..serializers import SubmissionSafeModelSerializer, SubmissionListSerializer


# new code for template START 18.9.20
def hidden_template_parser(template_str):
    lines = template_str.split("\n")
    lines = [line.replace(" ","") for line in lines if line!=""]
    labels = {}
    labels_flag = False

    category_name = ""

    for line in lines:
        if line == '/*' or line == '*/':
            continue

        if "//PREPENDEND" in line:
            labels_flag = False

        if labels_flag == True:
            if "[" in line:
                category_name = line[1:-1]
                if category_name not in labels:
                    labels[category_name] = {}
            else:
                problem_num = line.split('.')[0]
                label = line.split('.')[1].split('/')[0]
                assigned_score = line.split('/')[1][:-1]
                labels[category_name][problem_num] = [label.upper(), int(assigned_score)]

        if "//PREPENDBEGIN" in line:
            labels_flag = True
   
    return labels

def pred_parser(code):
    
    lines = code.split("\n")
    lines = [line.replace(" ","") for line in lines if line!=""] 
    
    preds = {}
    for line in lines:
        if "[" in line:
            category_name = line[1:-1]
            if category_name not in preds:
                preds[category_name] = {}
        else:
            problem_num = line.split('.')[0]
            pred = line.split('.')[1].split('/')[0]
            preds[category_name][problem_num] = [pred.upper()]
    return preds

def get_evals_json(preds, labels):

    _evals = {}
    sum_score = 0
    total_score = 0
    for category_name, problem_info_labels in labels.items():

        category_eval_score = 0
        category_total_score = 0

        if category_name not in _evals:
            _evals[category_name] = {}


        if category_name not in preds: # if there is no answer, all scores are 0
            for problem_num, _ in problem_info_labels.items(): 
                _evals[category_name][problem_num] = 0
                _evals[category_name]["category_sum_score"] = 0
            continue

        for problem_num, _ in problem_info_labels.items(): 
            labels_problem = labels[category_name][problem_num][0]
            labels_assigned_score = labels[category_name][problem_num][1]
            category_total_score += labels_assigned_score

            if problem_num not in preds[category_name]:
                _evals[category_name][problem_num] = 0
                continue

            preds_problem = preds[category_name][problem_num][0]

            if labels_problem.upper() == preds_problem.upper():
                _evals[category_name][problem_num] = labels_assigned_score
                category_eval_score += labels_assigned_score

            else:
                _evals[category_name][problem_num] = 0
                # category_eval_score += 0
                _evals[category_name]["category_sum_score"] = category_eval_score

        _evals[category_name]["category_total_score"] = category_total_score
        _evals[category_name]["category_sum_score"] = category_eval_score
        sum_score += category_eval_score
        total_score += category_total_score
        
    _evals["sum_score"] = sum_score
    _evals["total_score"] = total_score
    
    evals = {}    
    evals["evals"] = _evals
    evals["preds"] = preds
    evals["labels"] = labels
    return evals
# new code for template END 18.9.20


class SubmissionAPI_compile(APIView):
    def throttling(self, request):
        user_bucket = TokenBucket(key=str(request.user.id),
                                  redis_conn=cache, **SysOptions.throttling["user"])
        can_consume, wait = user_bucket.consume()
        if not can_consume:
            return "Please wait %d seconds" % (int(wait))

        ip_bucket = TokenBucket(key=request.session["ip"],
                                redis_conn=cache, **SysOptions.throttling["ip"])
        can_consume, wait = ip_bucket.consume()
        if not can_consume:
            return "Captcha is required"

    @validate_serializer(CreateSubmissionSerializer)
    @login_required
    def post(self, request):
        data = request.data
        hide_id = False
        problem = Problem.objects.get(id=data["problem_id"], contest_id=data.get("contest_id"), visible=True)

        result = Foo.judge(data, problem.id)

        return self.success(result)


class SubmissionAPI(APIView):
    def throttling(self, request):
        user_bucket = TokenBucket(key=str(request.user.id),
                                  redis_conn=cache, **SysOptions.throttling["user"])
        can_consume, wait = user_bucket.consume()
        if not can_consume:
            return "Please wait %d seconds" % (int(wait))

        ip_bucket = TokenBucket(key=request.session["ip"],
                                redis_conn=cache, **SysOptions.throttling["ip"])
        can_consume, wait = ip_bucket.consume()
        if not can_consume:
            return "Captcha is required"

    @validate_serializer(CreateSubmissionSerializer)
    @login_required
    def post(self, request):
        data = request.data
        hide_id = False
        if data.get("contest_id"):
            try:
                contest = Contest.objects.get(id=data["contest_id"], visible=True)
            except Contest.DoesNotExist:
                return self.error("Contest doesn't exist.")
            if contest.status == ContestStatus.CONTEST_ENDED:
                return self.error("The contest have ended")
            if not request.user.is_contest_admin(contest):
                if contest.status == ContestStatus.CONTEST_NOT_START:
                    return self.error("Contest have not started")
                user_ip = ipaddress.ip_address(request.session.get("ip"))
                if contest.allowed_ip_ranges:
                    if not any(user_ip in ipaddress.ip_network(cidr, strict=False) for cidr in contest.allowed_ip_ranges):
                        return self.error("Your IP is not allowed in this contest")

            if not contest.problem_details_permission(request.user):
                hide_id = True

        if data.get("captcha"):
            if not Captcha(request).check(data["captcha"]):
                return self.error("Invalid captcha")
        error = self.throttling(request)
        if error:
            return self.error(error)

        try:
            problem = Problem.objects.get(id=data["problem_id"], contest_id=data.get("contest_id"), visible=True)
        except Problem.DoesNotExist:
            return self.error("Problem not exist")

        # new code for O/X test 18.9.20
        ox_result_jsonb = None
        if str(data["language"]) == "PlainText":
            template_str = problem.template["PlainText"]
            labels = hidden_template_parser(str(template_str))
            preds = pred_parser(str(data["code"]))
            evals = get_evals_json(preds, labels)
            ox_result_jsonb = evals

        submission = Submission.objects.create(user_id=request.user.id,
                                               username=request.user.username,
                                               language=data["language"],
                                               code=data["code"],
                                               problem_id=problem.id,
                                               ip=request.session["ip"],
                                               contest_id=data.get("contest_id"),
                                               ox_result_jsonb=ox_result_jsonb)
        # use this for debug
        # JudgeDispatcher(submission.id, problem.id).judge()
        judge_task.delay(submission.id, problem.id)
        if hide_id:
            return self.success()
        else:
            return self.success({"submission_id": submission.id})

    @login_required
    def get(self, request):
        submission_id = request.GET.get("id")
        if not submission_id:
            return self.error("Parameter id doesn't exist")
        try:
            submission = Submission.objects.select_related("problem").get(id=submission_id)
        except Submission.DoesNotExist:
            return self.error("Submission doesn't exist")
        if not submission.check_user_permission(request.user):
            return self.error("No permission for this submission")

        if submission.problem.rule_type == ProblemRuleType.OI or request.user.is_admin_role():
            submission_data = SubmissionModelSerializer(submission).data
        else:
            submission_data = SubmissionSafeModelSerializer(submission).data
        # 是否有权限取消共享
        submission_data["can_unshare"] = submission.check_user_permission(request.user, check_share=False)
        return self.success(submission_data)

    @validate_serializer(ShareSubmissionSerializer)
    @login_required
    def put(self, request):
        """
        share submission
        """
        try:
            submission = Submission.objects.select_related("problem").get(id=request.data["id"])
        except Submission.DoesNotExist:
            return self.error("Submission doesn't exist")
        if not submission.check_user_permission(request.user, check_share=False):
            return self.error("No permission to share the submission")
        if submission.contest and submission.contest.status == ContestStatus.CONTEST_UNDERWAY:
            return self.error("Can not share submission now")
        submission.shared = request.data["shared"]
        submission.save(update_fields=["shared"])
        return self.success()


class SubmissionListAPI(APIView):
    def get(self, request):
        if not request.GET.get("limit"):
            return self.error("Limit is needed")
        if request.GET.get("contest_id"):
            return self.error("Parameter error")

        submissions = Submission.objects.filter(contest_id__isnull=True).select_related("problem__created_by")
        problem_id = request.GET.get("problem_id")
        myself = request.GET.get("myself")
        result = request.GET.get("result")
        username = request.GET.get("username")
        if problem_id:
            try:
                problem = Problem.objects.get(_id=problem_id, contest_id__isnull=True, visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem doesn't exist")
            submissions = submissions.filter(problem=problem)
        if (myself and myself == "1") or not SysOptions.submission_list_show_all:
            submissions = submissions.filter(user_id=request.user.id)
        elif username:
            submissions = submissions.filter(username__icontains=username)
        if result:
            submissions = submissions.filter(result=result)
        data = self.paginate_data(request, submissions)
        data["results"] = SubmissionListSerializer(data["results"], many=True, user=request.user).data
        return self.success(data)


class ContestSubmissionListAPI(APIView):
    @check_contest_permission(check_type="submissions")
    def get(self, request):
        if not request.GET.get("limit"):
            return self.error("Limit is needed")

        contest = self.contest
        submissions = Submission.objects.filter(contest_id=contest.id).select_related("problem__created_by")
        problem_id = request.GET.get("problem_id")
        myself = request.GET.get("myself")
        result = request.GET.get("result")
        username = request.GET.get("username")
        if problem_id:
            try:
                problem = Problem.objects.get(_id=problem_id, contest_id=contest.id, visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem doesn't exist")
            submissions = submissions.filter(problem=problem)

        if myself and myself == "1":
            submissions = submissions.filter(user_id=request.user.id)
        elif username:
            submissions = submissions.filter(username__icontains=username)
        if result:
            submissions = submissions.filter(result=result)

        # filter the test submissions submitted before contest start
        if contest.status != ContestStatus.CONTEST_NOT_START:
            submissions = submissions.filter(create_time__gte=contest.start_time)

        # 封榜的时候只能看到自己的提交
        if contest.rule_type == ContestRuleType.ACM:
            if not contest.real_time_rank and not request.user.is_contest_admin(contest):
                submissions = submissions.filter(user_id=request.user.id)

        data = self.paginate_data(request, submissions)
        data["results"] = SubmissionListSerializer(data["results"], many=True, user=request.user).data
        return self.success(data)


class SubmissionExistsAPI(APIView):
    def get(self, request):
        if not request.GET.get("problem_id"):
            return self.error("Parameter error, problem_id is required")
        return self.success(request.user.is_authenticated() and
                            Submission.objects.filter(problem_id=request.GET["problem_id"],
                                                      user_id=request.user.id).exists())

class SubmissionByUserAPI(APIView):
    def get(self, request):
        if not request.GET.get("userId"):
            return self.error("no userId")

        submissions = Submission.objects.filter(contest_id__isnull=True).select_related("problem__created_by")
        u_id = request.GET.get("userId")
        submissions = submissions.filter(user_id=u_id)
        data = self.paginate_data(request, submissions)
        data["results"] = SubmissionListSerializer(data["results"], many=True, user=request.user).data
        return self.success(data)
