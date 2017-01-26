import dateutil.parser
from utils.api import APIView, validate_serializer
from ..serializers import CreateConetestSeriaizer, ContestSerializer
from ..models import Contest


class ContestAPI(APIView):
    @validate_serializer(CreateConetestSeriaizer)
    def post(self, request):
        data = request.data
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        data["created_by"] = request.user
        print(data)
        Contest.objects.create(**data)
        print(request.data)
        return self.success()

    def get(self, request):
        return self.success(ContestSerializer(Contest.objects.all(), many=True).data)
