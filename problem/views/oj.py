from django.db.models import Q
from utils.api import APIView
from account.decorators import check_contest_permission
from ..models import ProblemTag, Problem, ContestProblem, ProblemRuleType
from ..serializers import ProblemSerializer, TagSerializer
from ..serializers import ContestProblemSerializer
from contest.models import ContestRuleType


class ProblemTagAPI(APIView):
    def get(self, request):
        return self.success(TagSerializer(ProblemTag.objects.all(), many=True).data)


class ProblemAPI(APIView):
    def get(self, request):
        # 问题详情页
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by").get(_id=problem_id, visible=True)
                return self.success(ProblemSerializer(problem).data)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        limit = request.GET.get("limit")
        if not limit:
            return self.error("Limit is needed")

        problems = Problem.objects.select_related("created_by").filter(visible=True)
        # 按照标签筛选
        tag_text = request.GET.get("tag")
        if tag_text:
            try:
                tag = ProblemTag.objects.get(name=tag_text)
            except ProblemTag.DoesNotExist:
                return self.error("The Tag does not exist.")
            problems = tag.problem_set.all().filter(visible=True)

        # 搜索的情况
        keyword = request.GET.get("keyword", "").strip()
        if keyword:
            problems = problems.filter(Q(title__contains=keyword) | Q(description__contains=keyword))

        # 难度筛选
        difficulty_rank = request.GET.get("difficulty")
        if difficulty_rank:
            problems = problems.filter(difficulty=difficulty_rank)
        # 根据profile 为做过的题目添加标记
        data = self.paginate_data(request, problems, ProblemSerializer)
        if request.user.id:
            profile = request.user.userprofile
            acm_problems_status = profile.acm_problems_status.get("problems", {})
            oi_problems_status = profile.oi_problems_status.get("problems", {})
            for problem in data["results"]:
                if problem["rule_type"] == ProblemRuleType.ACM:
                    problem["my_status"] = acm_problems_status.get(problem["_id"], None)
                else:
                    problem["my_status"] = oi_problems_status.get(problem["_id"], None)
        return self.success(data)


class ContestProblemAPI(APIView):
    @check_contest_permission
    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = ContestProblem.objects.select_related("created_by").get(_id=problem_id, contest=self.contest,
                                                                                  visible=True)
            except ContestProblem.DoesNotExist:
                return self.error("Problem does not exist.")
            return self.success(ContestProblemSerializer(problem).data)

        contest_problems = ContestProblem.objects.select_related("created_by").filter(contest=self.contest,
                                                                                      visible=True)
        # 根据profile， 为做过的题目添加标记
        data = ContestProblemSerializer(contest_problems, many=True).data
        if request.user.id:
            profile = request.user.userprofile
            if self.contest.rule_type == ContestRuleType.ACM:
                problems_status = profile.acm_problems_status.get("contest_problems", {})
            else:
                problems_status = profile.oi_problems_status.get("contest_problems", {})
            for problem in data:
                problem["my_status"] = problems_status.get(problem["_id"], None)
        return self.success(ContestProblemSerializer(contest_problems, many=True).data)
