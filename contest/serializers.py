from utils.api import DateTimeTZField, UsernameSerializer, serializers

from .models import Contest, ContestAnnouncement, ContestRuleType


class CreateConetestSeriaizer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    description = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    rule_type = serializers.ChoiceField(choices=[ContestRuleType.ACM, ContestRuleType.OI])
    password = serializers.CharField(allow_blank=True, max_length=32)
    visible = serializers.BooleanField()
    real_time_rank = serializers.BooleanField()


class ContestSerializer(serializers.ModelSerializer):
    start_time = DateTimeTZField()
    end_time = DateTimeTZField()
    create_time = DateTimeTZField()
    last_update_time = DateTimeTZField()
    created_by = UsernameSerializer()
    status = serializers.CharField()
    contest_type = serializers.CharField()

    class Meta:
        model = Contest
        exclude = ('password', 'visible')

class EditConetestSeriaizer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=128)
    description = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    password = serializers.CharField(allow_blank=True, allow_null=True, max_length=32)
    visible = serializers.BooleanField()
    real_time_rank = serializers.BooleanField()


class ContestAnnouncementSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()
    create_time = DateTimeTZField()

    class Meta:
        model = ContestAnnouncement


class CreateContestAnnouncementSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    content = serializers.CharField()
    contest_id = serializers.IntegerField()
