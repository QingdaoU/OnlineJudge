# coding=utf-8
import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.http import HttpResponse

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .decorators import login_required


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


class EmailCheckTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("email_check_api")
        User.objects.create(email="11@qq.com")

    def test_invalid_data(self):
        response = self.client.post(self.url, data={"email000": "11@qq.com"})
        self.assertEqual(response.data["code"], 1)

    def test_email_exists(self):
        response = self.client.post(self.url, data={"email": "11@qq.com"})
        self.assertEqual(response.data, {"code": 0, "data": True})

    def test_email_does_not_exist(self):
        response = self.client.post(self.url, data={"email": "33@qq.com"})
        self.assertEqual(response.data, {"code": 0, "data": False})


class UserRegisterAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_register_api")

    def test_invalid_data(self):
        data = {"username": "test", "real_name": "TT"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_short_password(self):
        data = {"username": "test", "real_name": "TT", "password": "qq", "email": "6060@qq.com"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_same_username(self):
        User.objects.create(username="aa")
        data = {"username": "aa", "real_name": "ww", "password": "zzzzzzz", "email": "6060@qq.com"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"用户名已存在"})

    def test_same_email(self):
        User.objects.create(username="bb", email="8080@qq.com")
        data = {"username": "aa", "real_name": "ww", "password": "zzzzzzz", "email": "8080@qq.com"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该邮箱已被注册，请换其他邮箱进行注册"})

    def test_success_email(self):
        data = {"username": "cc", "real_name": "dd", "password": "xxxxxx", "email": "9090@qq.com"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"注册成功！"})


class UserChangePasswordAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_change_password_api")
        user = User.objects.create(username="test")
        user.set_password("aaabbb")
        user.save()

    def test_error_old_password(self):
        data = {"username": "test", "old_password": "aaaccc", "new_password": "aaaddd"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"密码不正确，请重新修改！"})

    def test_invalid_data_format(self):
        data = {"username": "test", "old_password": "aaa", "new_password": "aaaddd"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_username_does_not_exist(self):
        data = {"username": "test1", "old_password": "aaabbb", "new_password": "aaaddd"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_success_change_password(self):
        data = {"username": "test", "old_password": "aaabbb", "new_password": "aaaccc"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"用户密码修改成功！"})


@login_required
def login_required_FBV_test_without_args(request):
    return HttpResponse("function based view test1")


@login_required
def login_required_FBC_test_with_args(request, problem_id):
    return HttpResponse(problem_id)


class LoginRequiredCBVTestWithoutArgs(APIView):
    @login_required
    def get(self, request):
        return HttpResponse("class based view login required test1")

class LoginRequiredCBVTestWithArgs(APIView):
    @login_required
    def get(self, request, problem_id):
        return HttpResponse(problem_id)


class LoginRequiredDecoratorTest(TestCase):
    urls = 'account.test_urls'

    def setUp(self):
        self.client = Client()
        user = User.objects.create(username="test")
        user.set_password("test")
        user.save()

    def test_fbv_without_args(self):
        # 没登陆
        response = self.client.get("/test/fbv/1/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/test/fbv/1/")
        self.assertEqual(response.content, "function based view test1")

    def test_fbv_with_args(self):
        # 没登陆
        response = self.client.get("/test/fbv/1024/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/test/fbv/1024/")
        self.assertEqual(response.content, "1024")

    def test_cbv_without_args(self):
        # 没登陆
        response = self.client.get("/test/cbv/1/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/test/cbv/1/")
        self.assertEqual(response.content, "class based view login required test1")

    def test_cbv_with_args(self):
        # 没登陆
        response = self.client.get("/test/cbv/1024/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content), {"code": 1, "data": u"请先登录"})

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/test/cbv/1024/")
        self.assertEqual(response.content, "1024")
