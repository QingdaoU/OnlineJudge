from utils.api import serializers

from .models import SMTPConfig, WebsiteConfig


class EditSMTPConfigSerializer(serializers.Serializer):
    server = serializers.CharField(max_length=128)
    port = serializers.IntegerField(default=25)
    email = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)
    tls = serializers.BooleanField()


class CreateSMTPConfigSerializer(EditSMTPConfigSerializer):
    password = serializers.CharField(max_length=128)
    

class SMTPConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPConfig
        exclude = ["id", "password"]
        

class TestSMTPConfigSerializer(serializers.Serializer):
    email = serializers.EmailField()
    

class CreateEditWebsiteConfigSerializer(serializers.Serializer):
    base_url = serializers.CharField(max_length=128)
    name = serializers.CharField(max_length=32)
    name_shortcut = serializers.CharField(max_length=32)
    website_footer = serializers.CharField(max_length=1024)
    allow_register = serializers.BooleanField()
    submission_list_show_all = serializers.BooleanField()


class WebsiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteConfig
        exclude = ["id"]