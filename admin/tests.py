# coding=utf-8
import json

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from account.models import User


def middleware_test_func(request):
    return HttpResponse(json.dumps({"code": 0}))


class AdminRequiredMiddlewareTest(TestCase):
    urls = "admin.test_urls"

    def setUp(self):
        admin_user = User.objects.create(username="test", admin_type=0)
        admin_user.set_password("test")
        admin_user.save()

        admin_user = User.objects.create(username="test1", admin_type=1)
        admin_user.set_password("test")
        admin_user.save()
        super_admin_user = User.objects.create(username="test2", admin_type=2)
        super_admin_user.set_password("test")
        super_admin_user.save()

        self.client = Client()

    def test_need_admin_login(self):
        url = "/admin/"
        response = self.client.get(url)
        self.assertRedirects(response, "/login/")

        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertRedirects(response, "/login/")
        self.client.logout()

        self.client.login(username="test1", password="test")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "admin/admin.html")
        self.client.logout()

        self.client.login(username="test2", password="test")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "admin/admin.html")

    def test_need_admin_login_ajax(self):
        url = "/api/admin/test/"
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content), {"code": 1, "data": u"请先登录"})

        self.client.login(username="test", password="test")
        rresponse = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content), {"code": 1, "data": u"请先登录"})
        self.client.logout()

        self.client.login(username="test1", password="test")
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content)["code"], 0)
        self.client.logout()

        self.client.login(username="test2", password="test")
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content)["code"], 0)


class AdminTemplateViewTest(TestCase):
    def setUp(self):
        super_admin_user = User.objects.create(username="test", admin_type=2)
        super_admin_user.set_password("test")
        super_admin_user.save()

        self.client = Client()
        self.client.login(username="test", password="test")

    def test_file_exists(self):
        response = self.client.get("/admin/template/index/index.html")
        self.assertEqual(response.status_code, 200)

    def test_file_does_not_exist(self):
        response = self.client.get("/admin/template/index/index123.html")
        self.assertEqual(response.status_code, 200)
        self.assertHTMLEqual(response.content, u"模板不存在")
