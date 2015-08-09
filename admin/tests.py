# coding=utf-8
import json
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from account.models import User


def middleware_test_func(request):
    return HttpResponse(json.dumps({"code": 0}))


class AdminRequiredMidlewareTest(TestCase):
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

