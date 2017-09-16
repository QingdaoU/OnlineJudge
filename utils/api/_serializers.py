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
