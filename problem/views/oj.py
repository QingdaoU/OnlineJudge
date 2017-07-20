from django.db.models import Q
from utils.api import APIView
from account.decorators import check_contest_permission
from ..models import ProblemTag, Problem, ContestProblem
from ..serializers import ProblemSerializer, TagSerializer
from ..serializers import ContestProblemSerializer


class ProblemTagAPI(APIView):
    def get(self, request):
        return self.success(TagSerializer(ProblemTag.objects.all(), many=True).data)


class ProblemAPI(APIView):
    def get(self, request):
        # 问题详情页
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.get(_id=problem_id, visible=True)
                return self.success(ProblemSerializer(problem).data)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        problems = Problem.objects.filter(visible=True)
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

        return self.success(self.paginate_data(request, problems, ProblemSerializer))


class ContestProblemAPI(APIView):
    @check_contest_permission
    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = ContestProblem.objects.get(_id=problem_id, contest=self.contest, visible=True)
            except ContestProblem.DoesNotExist:
                return self.error("Problem does not exist.")
            return self.success(ContestProblemSerializer(problem).data)

        contest_problems = ContestProblem.objects.filter(contest=self.contest, visible=True)
        return self.success(ContestProblemSerializer(contest_problems, many=True).data)
