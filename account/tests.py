# coding=utf-8
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from rest_framework.test import APITestCase, APIClient

from .models import User


class UserLoginTest(TestCase):
    def test_login_page(self):
        client = Client()
        response = client.get(reverse("user_login_page"))
        self.assertTemplateUsed(response, "oj/account/login.html")


class UserLoginAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_login_api")
        user = User.objects.create(username="test")
        user.set_password("test")
        user.save()

    def test_invalid_data(self):
        data = {"username": "test"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_error_username_or_password(self):
        error_data = {"username": "test", "password": "test11"}
        response = self.client.post(self.url, data=error_data)
        self.assertEqual(response.data, {"code": 1, "data": u"用户名或密码错误"})

    def test_success_login(self):
        data = {"username": "test", "password": "test"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"登录成功"})


class UsernameCheckTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("username_check_api")
        User.objects.create(username="testtest")

    def test_invalid_data(self):
        response = self.client.post(self.url, data={"username111": "testtest"})
        self.assertEqual(response.data["code"], 1)

    def test_username_exists(self):
        response = self.client.post(self.url, data={"username": "testtest"})
        self.assertEqual(response.data, {"code": 0, "data": True})

    def test_username_does_not_exist(self):
        response = self.client.post(self.url, data={"username": "testtest123"})
        self.assertEqual(response.data, {"code": 0, "data": False})
