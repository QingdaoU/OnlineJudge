from utils.api.tests import APITestCase

from .models import SMTPConfig, WebsiteConfig


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
        smtp = SMTPConfig.objects.first()
        self.assertEqual(smtp.password, self.password)
        self.assertEqual(smtp.server, "smtp1.test.com")
        self.assertEqual(smtp.email, "test2@test.com")

    def test_edit_without_password1(self):
        self.test_create_smtp_config()
        data = {"server": "smtp.test.com", "email": "test@test.com", "port": 465,
                "tls": True, "password": ""}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)
        self.assertEqual(SMTPConfig.objects.first().password, self.password)

    def test_edit_with_password(self):
        self.test_create_smtp_config()
        data = {"server": "smtp1.test.com", "email": "test2@test.com", "port": 465,
                "tls": True, "password": "newpassword"}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)
        smtp = SMTPConfig.objects.first()
        self.assertEqual(smtp.password, "newpassword")
        self.assertEqual(smtp.server, "smtp1.test.com")
        self.assertEqual(smtp.email, "test2@test.com")


class WebsiteConfigAPITest(APITestCase):
    def test_create_website_config(self):
        user = self.create_super_admin()
        url = self.reverse("website_config_api")
        data = {"base_url": "http://test.com", "name": "test name",
                "name_shortcut": "test oj", "website_footer": "<a>test</a>",
                "allow_register": True, "submission_list_show_all": False}
        resp = self.client.post(url, data=data)
        self.assertSuccess(resp)

    def test_edit_website_config(self):
        user = self.create_super_admin()
        url = self.reverse("website_config_api")
        data = {"base_url": "http://test.com", "name": "test name",
                "name_shortcut": "test oj", "website_footer": "<a>test</a>",
                "allow_register": True, "submission_list_show_all": False}
        resp = self.client.post(url, data=data)
        self.assertSuccess(resp)

    def test_get_website_config(self):
        # do not need to login
        url = self.reverse("website_info_api")
        resp = self.client.get(url)
        self.assertSuccess(resp)
        self.assertEqual(resp.data["data"]["name_shortcut"], "oj")
