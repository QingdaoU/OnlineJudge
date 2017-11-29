from rest_framework import serializers


class DateTimeTZField(serializers.DateTimeField):
    def to_representation(self, value):
        # value = timezone.localtime(value)
        return super(DateTimeTZField, self).to_representation(value)


class IDOnlySerializer(serializers.Serializer):
    id = serializers.IntegerField()


class UsernameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    real_name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.is_admin_role = kwargs.pop("is_admin_role", False)
        super().__init__(*args, **kwargs)

    def get_real_name(self, obj):
        return obj.userprofile.real_name if self.is_admin_role else None
