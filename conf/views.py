import os
import re
import hashlib
import shutil

from django.utils import timezone
from django.conf import settings

from account.decorators import super_admin_required
from problem.models import Problem
from judge.dispatcher import process_pending_task
from judge.languages import languages, spj_languages
from options.options import SysOptions
from utils.api import APIView, CSRFExemptAPIView, validate_serializer
from utils.shortcuts import send_email
from .models import JudgeServer
from .serializers import (CreateEditWebsiteConfigSerializer,
                          CreateSMTPConfigSerializer, EditSMTPConfigSerializer,
                          JudgeServerHeartbeatSerializer,
                          JudgeServerSerializer, TestSMTPConfigSerializer)


class SMTPAPI(APIView):
    @super_admin_required
    def get(self, request):
        smtp = SysOptions.smtp_config
        if not smtp:
            return self.success(None)
        smtp.pop("password")
        return self.success(smtp)

    @validate_serializer(CreateSMTPConfigSerializer)
    @super_admin_required
    def post(self, request):
        SysOptions.smtp_config = request.data
        return self.success()

    @validate_serializer(EditSMTPConfigSerializer)
    @super_admin_required
    def put(self, request):
        smtp = SysOptions.smtp_config
        data = request.data
        for item in ["server", "port", "email", "tls"]:
            smtp[item] = data[item]
        if "password" in data:
            smtp["password"] = data["password"]
        SysOptions.smtp_config = smtp
        return self.success()


class SMTPTestAPI(APIView):
    @super_admin_required
    @validate_serializer(TestSMTPConfigSerializer)
    def post(self, request):
        if not SysOptions.smtp_config:
            return self.error("Please setup SMTP config at first")
        try:
            send_email(smtp_config=SysOptions.smtp_config,
                       from_name=SysOptions.website_name_shortcut,
                       to_name=request.user.username,
                       to_email=request.data["email"],
                       subject="You have successfully configured SMTP",
                       content="You have successfully configured SMTP")
        except Exception as e:
            # guess error message encoding
            msg = e.smtp_error
            try:
                # qq mail
                msg = msg.decode("gbk")
            except Exception:
                msg = msg.decode("utf-8", "ignore")
            return self.error(msg)
        return self.success()


class WebsiteConfigAPI(APIView):
    def get(self, request):
        ret = {key: getattr(SysOptions, key) for key in
               ["website_base_url", "website_name", "website_name_shortcut",
                "website_footer", "allow_register", "submission_list_show_all"]}
        return self.success(ret)

    @validate_serializer(CreateEditWebsiteConfigSerializer)
    @super_admin_required
    def post(self, request):
        for k, v in request.data.items():
            setattr(SysOptions, k, v)
        return self.success()


class JudgeServerAPI(APIView):
    @super_admin_required
    def get(self, request):
        servers = JudgeServer.objects.all().order_by("-last_heartbeat")
        return self.success({"token": SysOptions.judge_server_token,
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
        data = request.data
        client_token = request.META.get("HTTP_X_JUDGE_SERVER_TOKEN")
        if hashlib.sha256(SysOptions.judge_server_token.encode("utf-8")).hexdigest() != client_token:
            return self.error("Invalid token")
        service_url = data.get("service_url")

        try:
            server = JudgeServer.objects.get(hostname=data["hostname"])
            server.judger_version = data["judger_version"]
            server.cpu_core = data["cpu_core"]
            server.memory_usage = data["memory"]
            server.cpu_usage = data["cpu"]
            server.service_url = service_url
            server.ip = request.META["HTTP_X_REAL_IP"]
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
            # 新server上线 处理队列中的，防止没有新的提交而导致一直waiting
            process_pending_task()

        return self.success()


class LanguagesAPI(APIView):
    def get(self, request):
        return self.success({"languages": languages, "spj_languages": spj_languages})


class TestCasePruneAPI(APIView):
    @super_admin_required
    def get(self, request):
        """
        return isolated test_case list
        """
        ret_data = []
        dir_to_be_removed = self.get_orphan_ids()

        # return an iterator
        for d in os.scandir(settings.TEST_CASE_DIR):
            if d.name in dir_to_be_removed:
                ret_data.append({"id": d.name, "create_time": d.stat().st_ctime})
        return self.success(ret_data)

    @super_admin_required
    def delete(self, request):
        test_case_id = request.GET.get("id")
        if test_case_id:
            self.delete_one(test_case_id)
            return self.success()
        for id in self.get_orphan_ids():
            self.delete_one(id)
        return self.success()

    @staticmethod
    def get_orphan_ids():
        db_ids = Problem.objects.all().values_list("test_case_id", flat=True)
        disk_ids = os.listdir(settings.TEST_CASE_DIR)
        test_case_re = re.compile(r"^[a-zA-Z0-9]{32}$")
        disk_ids = filter(lambda f: test_case_re.match(f), disk_ids)
        return list(set(disk_ids) - set(db_ids))

    @staticmethod
    def delete_one(id):
        test_case_dir = os.path.join(settings.TEST_CASE_DIR, id)
        if os.path.isdir(test_case_dir):
            shutil.rmtree(test_case_dir, ignore_errors=True)
