from utils.api import APIView

from .models import ProblemTag


class ProblemTagAPI(APIView):
    def get(self, request):
        return self.success([item.name for item in ProblemTag.objects.all().order_by("id")])
