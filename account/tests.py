# coding=utf-8
import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.http import HttpResponse
from django.contrib import auth

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User, SUPER_ADMIN
from .decorators import login_required, admin_required


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


class UserAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_admin_api")
        user = User.objects.create(username="testx", real_name="xx", admin_type=SUPER_ADMIN)
        user.set_password("testxx")
        user.save()

    def test_success_get_data(self):
        self.client.login(username="testx", password="testxx")
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    def test_error_admin_type(self):
        self.client.login(username="testx", password="testxx")
        response = self.client.get(self.url + "?admin_type=error")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})

    def test_query_by_keyword(self):
        self.client.login(username="testx", password="testxx")
        user1 = User.objects.create(username="test1", real_name="aa")
        user1.set_password("testaa")
        user1.save()

        user2 = User.objects.create(username="test2", real_name="bb")
        user2.set_password("testbb")
        user2.save()

        user3 = User.objects.create(username="test3", real_name="cc")
        user3.set_password("testcc")
        user3.save()

        response = self.client.get(self.url + "?keyword=test1")
        self.assertEqual(response.data["code"], 0)

    def test_put_invalid_data(self):
        self.client.login(username="testx", password="testxx")
        data = {"username": "test", "password": "testaa", "email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_user_does_not_exist(self):
        self.client.login(username="testx", password="testxx")
        data = {"id": 2, "username": "test0", "real_name": "test00",
                "password": "testaa","email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该用户不存在！"})

    def test_success_user_edit_not_password(self):
        self.client.login(username="testx", password="testxx")
        data = {"id": 1, "username": "test0", "real_name": "test00",
                "email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_success_user_edit_change_password(self):
        self.client.login(username="testx", password="testxx")
        data = {"id": 1, "username": "test0", "real_name": "test00", "password": "111111",
                "email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
        self.assertIsNotNone(auth.authenticate(username="test0", password="111111"))


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
        response = self.client.get("/login_required_test/fbv/1/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/login_required_test/fbv/1/")
        self.assertEqual(response.content, "function based view test1")

    def test_fbv_with_args(self):
        # 没登陆
        response = self.client.get("/login_required_test/fbv/1024/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/login_required_test/fbv/1024/")
        self.assertEqual(response.content, "1024")

    def test_cbv_without_args(self):
        # 没登陆
        response = self.client.get("/login_required_test/cbv/1/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/login_required_test/cbv/1/")
        self.assertEqual(response.content, "class based view login required test1")

    def test_cbv_with_args(self):
        # 没登陆
        response = self.client.get("/login_required_test/cbv/1024/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content), {"code": 1, "data": u"请先登录"})

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/login_required_test/cbv/1024/")
        self.assertEqual(response.content, "1024")


@admin_required
def admin_required_FBV_test_without_args(request):
    return HttpResponse("function based view test1")


@admin_required
def admin_required_FBC_test_with_args(request, problem_id):
    return HttpResponse(problem_id)


class AdminRequiredCBVTestWithoutArgs(APIView):
    @admin_required
    def get(self, request):
        return HttpResponse("class based view login required test1")


class AdminRequiredCBVTestWithArgs(APIView):
    @admin_required
    def get(self, request, problem_id):
        return HttpResponse(problem_id)


class AdminRequiredDecoratorTest(TestCase):
    urls = 'account.test_urls'

    def setUp(self):
        self.client = Client()
        user = User.objects.create(username="test")
        user.admin_type = 1
        user.set_password("test")
        user.save()

    def test_fbv_without_args(self):
        # 没登陆
        response = self.client.get("/admin_required_test/fbv/1/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/fbv/1/")
        self.assertEqual(response.content, "function based view test1")

    def test_fbv_with_args(self):
        # 没登陆
        response = self.client.get("/admin_required_test/fbv/1024/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/fbv/1024/")
        self.assertEqual(response.content, "1024")

    def test_cbv_without_args(self):
        # 没登陆
        response = self.client.get("/admin_required_test/cbv/1/")
        self.assertTemplateUsed(response, "utils/error.html")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/cbv/1/")
        self.assertEqual(response.content, "class based view login required test1")

    def test_cbv_with_args(self):
        # 没登陆
        response = self.client.get("/admin_required_test/cbv/1024/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content), {"code": 1, "data": u"需要管理员权限"})

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/cbv/1024/")
        self.assertEqual(response.content, "1024")
