import hashlib

from django.utils import timezone

from account.decorators import super_admin_required
from judge.languages import languages, spj_languages
from utils.api import APIView, CSRFExemptAPIView, validate_serializer
from utils.shortcuts import rand_str

from .models import JudgeServer, JudgeServerToken, SMTPConfig, WebsiteConfig
from .serializers import (CreateEditWebsiteConfigSerializer,
                          CreateSMTPConfigSerializer, EditSMTPConfigSerializer,
                          JudgeServerHeartbeatSerializer,
                          JudgeServerSerializer, SMTPConfigSerializer,
                          TestSMTPConfigSerializer, WebsiteConfigSerializer)


class SMTPAPI(APIView):
    @super_admin_required
    def get(self, request):
        smtp = SMTPConfig.objects.first()
        if not smtp:
            return self.success(None)
        return self.success(SMTPConfigSerializer(smtp).data)

    @validate_serializer(CreateSMTPConfigSerializer)
    @super_admin_required
    def post(self, request):
        SMTPConfig.objects.all().delete()
        smtp = SMTPConfig.objects.create(**request.data)
        return self.success(SMTPConfigSerializer(smtp).data)

    @validate_serializer(EditSMTPConfigSerializer)
    @super_admin_required
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


class JudgeServerAPI(APIView):
    @super_admin_required
    def get(self, request):
        judge_server_token = JudgeServerToken.objects.first()
        if not judge_server_token:
            token = rand_str(12)
            JudgeServerToken.objects.create(token=token)
        else:
            token = judge_server_token.token
        servers = JudgeServer.objects.all().order_by("-last_heartbeat")
        return self.success({"token": token,
                             "servers": JudgeServerSerializer(servers, many=True).data})

    @super_admin_required
    def delete(self, request):
        hostname = request.GET.get("hostname")
        if hostname:
            JudgeServer.objects.filter(hostname=hostname).delete()
        return self.success()


class JudgeServerHeartbeatAPI(CSRFExemptAPIView):
    @validate_serializer(JudgeServerHeartbeatSerializer)
    def post(self, request):
        judge_server_token = JudgeServerToken.objects.first()
        if not judge_server_token:
            token = rand_str(12)
            JudgeServerToken.objects.create(token=token)
        else:
            token = judge_server_token.token
        data = request.data
        client_token = request.META.get("HTTP_X_JUDGE_SERVER_TOKEN")
        if hashlib.sha256(token.encode("utf-8")).hexdigest() != client_token:
            return self.error("Invalid token")
        service_url = data.get("service_url")

        try:
            server = JudgeServer.objects.get(hostname=data["hostname"])
            server.judger_version = data["judger_version"]
            server.cpu_core = data["cpu_core"]
            server.memory_usage = data["memory"]
            server.cpu_usage = data["cpu"]
            server.service_url = service_url
            server.ip = request.META["REMOTE_ADDR"]
            server.last_heartbeat = timezone.now()
            server.save()
        except JudgeServer.DoesNotExist:
            JudgeServer.objects.create(hostname=data["hostname"],
                                       judger_version=data["judger_version"],
                                       cpu_core=data["cpu_core"],
                                       memory_usage=data["memory"],
                                       cpu_usage=data["cpu"],
                                       ip=request.META["REMOTE_ADDR"],
                                       service_url=service_url,
                                       last_heartbeat=timezone.now(),
                                       )
        return self.success()


class LanguagesAPI(APIView):
    def get(self, request):
        return self.success({"languages": languages, "spj_languages": spj_languages})
