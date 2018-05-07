from utils.api import serializers
from utils.api._serializers import UsernameSerializer

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()

    class Meta:
        model = Group
        fields = "__all__"
