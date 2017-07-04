from .models import Submission
from account.models import User
from utils.api import serializers
from judge.languages import language_names


class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = serializers.ChoiceField(choices=language_names)
    code = serializers.CharField(max_length=20000)


class SubmissionModelSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    info = serializers.JSONField()
    statistic_info = serializers.JSONField()

    class Meta:
        model = Submission

    @staticmethod
    def get_username(obj):
        return User.objects.get(id=obj.user_id).username
