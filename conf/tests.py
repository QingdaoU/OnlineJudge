import hashlib

from django.utils import timezone

from options.options import SysOptions
from utils.api.tests import APITestCase
from .models import JudgeServer


class SMTPConfigTest(APITestCase):
    def setUp(self):
        self.user = self.create_super_admin()
        self.url = self.reverse("smtp_admin_api")
        self.password = "testtest"

    def test_create_smtp_config(self):
        data = {"server": "smtp.test.com", "email": "test@test.com", "port": 465,
                "tls": True, "password": self.password}
        resp = self.client.post(self.url, data=data)
        self.assertSuccess(resp)
        self.assertTrue("password" not in resp.data)
        return resp

    def test_edit_without_password(self):
        self.test_create_smtp_config()
        data = {"server": "smtp1.test.com", "email": "test2@test.com", "port": 465,
                "tls": True}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)

    def test_edit_without_password1(self):
        self.test_create_smtp_config()
        data = {"server": "smtp.test.com", "email": "test@test.com", "port": 465,
                "tls": True, "password": ""}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)

    def test_edit_with_password(self):
        self.test_create_smtp_config()
        data = {"server": "smtp1.test.com", "email": "test2@test.com", "port": 465,
                "tls": True, "password": "newpassword"}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)


class WebsiteConfigAPITest(APITestCase):
    def test_create_website_config(self):
        self.create_super_admin()
        url = self.reverse("website_config_api")
        data = {"website_base_url": "http://test.com", "website_name": "test name",
                "website_name_shortcut": "test oj", "website_footer": "<a>test</a>",
                "allow_register": True, "submission_list_show_all": False}
        resp = self.client.post(url, data=data)
        self.assertSuccess(resp)

    def test_edit_website_config(self):
        self.create_super_admin()
        url = self.reverse("website_config_api")
        data = {"website_base_url": "http://test.com", "website_name": "test name",
                "website_name_shortcut": "test oj", "website_footer": "<a>test</a>",
                "allow_register": True, "submission_list_show_all": False}
        resp = self.client.post(url, data=data)
        self.assertSuccess(resp)

    def test_get_website_config(self):
        # do not need to login
        url = self.reverse("website_info_api")
        resp = self.client.get(url)
        self.assertSuccess(resp)


class JudgeServerHeartbeatTest(APITestCase):
    def setUp(self):
        self.url = self.reverse("judge_server_heartbeat_api")
        self.data = {"hostname": "testhostname", "judger_version": "1.0.4", "cpu_core": 4,
                     "cpu": 90.5, "memory": 80.3, "action": "heartbeat"}
        self.token = "test"
        self.hashed_token = hashlib.sha256(self.token.encode("utf-8")).hexdigest()
        SysOptions.judge_server_token = self.token

    def test_new_heartbeat(self):
        resp = self.client.post(self.url, data=self.data, **{"HTTP_X_JUDGE_SERVER_TOKEN": self.hashed_token})
        self.assertSuccess(resp)
        server = JudgeServer.objects.first()
        self.assertEqual(server.ip, "127.0.0.1")
        self.assertEqual(server.service_url, None)

    def test_new_heartbeat_service_url(self):
        service_url = "http://1.2.3.4:8000/api/judge"
        data = self.data
        data["service_url"] = service_url
        resp = self.client.post(self.url, data=self.data, **{"HTTP_X_JUDGE_SERVER_TOKEN": self.hashed_token})
        self.assertSuccess(resp)
        server = JudgeServer.objects.first()
        self.assertEqual(server.service_url, service_url)

    def test_update_heartbeat(self):
        self.test_new_heartbeat()
        data = self.data
        data["judger_version"] = "2.0.0"
        resp = self.client.post(self.url, data=data, **{"HTTP_X_JUDGE_SERVER_TOKEN": self.hashed_token})
        self.assertSuccess(resp)
        self.assertEqual(JudgeServer.objects.get(hostname=self.data["hostname"]).judger_version, data["judger_version"])


class JudgeServerAPITest(APITestCase):
    def setUp(self):
        JudgeServer.objects.create(**{"hostname": "testhostname", "judger_version": "1.0.4",
                                      "cpu_core": 4, "cpu_usage": 90.5, "memory_usage": 80.3,
                                      "last_heartbeat": timezone.now()})
        self.url = self.reverse("judge_server_api")
        self.create_super_admin()

    def test_get_judge_server(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
        self.assertEqual(len(resp.data["data"]["servers"]), 1)

    def test_delete_judge_server(self):
        resp = self.client.delete(self.url + "?hostname=testhostname")
        self.assertSuccess(resp)
        self.assertFalse(JudgeServer.objects.filter(hostname="testhostname").exists())


class LanguageListAPITest(APITestCase):
    def test_get_languages(self):
        resp = self.client.get(self.reverse("language_list_api"))
        self.assertSuccess(resp)
