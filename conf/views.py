from utils.api import APIView, validate_serializer

from account.decorators import super_admin_required

from .models import SMTPConfig, WebsiteConfig
from .serializers import (WebsiteConfigSerializer, CreateEditWebsiteConfigSerializer,
                          CreateSMTPConfigSerializer, EditSMTPConfigSerializer,
                          SMTPConfigSerializer, TestSMTPConfigSerializer)


class SMTPAPI(APIView):
    @super_admin_required
    def get(self, request):
        smtp = SMTPConfig.objects.first()
        if not smtp:
            return self.success(None)
        return self.success(SMTPConfigSerializer(smtp).data)

    @super_admin_required
    @validate_serializer(CreateSMTPConfigSerializer)
    def post(self, request):
        SMTPConfig.objects.all().delete()
        smtp = SMTPConfig.objects.create(**request.data)
        return self.success(SMTPConfigSerializer(smtp).data)

    @super_admin_required
    @validate_serializer(EditSMTPConfigSerializer)
    def put(self, request):
        data = request.data
        smtp = SMTPConfig.objects.first()
        if not smtp:
            return self.error("SMTP config is missing")
        smtp.server = data["server"]
        smtp.port = data["port"]
        smtp.email = data["email"]
        smtp.tls = data["tls"]
        if data.get("password"):
            smtp.password = data["password"]
        smtp.save()
        return self.success(SMTPConfigSerializer(smtp).data)


class SMTPTestAPI(APIView):
    @super_admin_required
    @validate_serializer(TestSMTPConfigSerializer)
    def post(self, request):
        email = request.data["email"]
        # todo: test send email
        return self.success({"result": True})


class WebsiteConfigAPI(APIView):
    def get(self, request):
        config = WebsiteConfig.objects.first()
        if not config:
            config = WebsiteConfig.objects.create()
        return self.success(WebsiteConfigSerializer(config).data)

    @validate_serializer(CreateEditWebsiteConfigSerializer)
    @super_admin_required
    def post(self, request):
        data = request.data
        WebsiteConfig.objects.all().delete()
        config = WebsiteConfig.objects.create(**data)
        return self.success(WebsiteConfigSerializer(config).data)
