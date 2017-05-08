from utils.api import serializers

# from account.models import User
# from .models import Submission


class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=20000)
