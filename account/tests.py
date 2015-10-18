# coding=utf-8
import json
import time

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.http import HttpResponse
from django.contrib import auth
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView

from .models import User, SUPER_ADMIN, REGULAR_USER, ADMIN
from .decorators import login_required, admin_required, super_admin_required


class UserLoginTest(TestCase):
    def test_login_page(self):
        client = Client()
        response = client.get(reverse("user_login_page"))
        self.assertTemplateUsed(response, "oj/account/login.html")


def create_user(username="test", real_name="test_real_name", email="test@qq.com",
                password="111111", admin_type=REGULAR_USER):
    user = User.objects.create(username=username, real_name=real_name, email=email, admin_type=admin_type)
    user.set_password(password)
    user.save()
    return user


def set_captcha(session):
    session["_django_captcha_key"] = "aaaa"
    session["_django_captcha_expires_time"] = time.time() + 10000
    session.save()


class UserLoginAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_login_api")
        self.user = create_user()
        set_captcha(self.client.session)

    def test_invalid_data(self):
        data = {"username": "test"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_captcha(self):
        error_data = {"username": "test", "password": "test11", "captcha": "1111"}
        response = self.client.post(self.url, data=error_data)
        self.assertEqual(response.data, {"code": 1, "data": u"验证码错误"})

    def test_error_username_or_password(self):
        error_data = {"username": "test", "password": "test11", "captcha": "aaaa"}
        response = self.client.post(self.url, data=error_data)
        self.assertEqual(response.data, {"code": 1, "data": u"用户名或密码错误"})

    def test_login_successfully(self):
        data = {"username": "test", "password": "111111", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"登录成功"})


class UsernameCheckTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("username_check_api")
        create_user()

    def test_invalid_data(self):
        response = self.client.get(self.url, data={"username111": "testtest"})
        self.assertEqual(response.status_code, 200)

    def test_username_exists(self):
        response = self.client.get(self.url, data={"username": "test"})
        self.assertEqual(response.status_code, 400)

    def test_username_does_not_exist(self):
        response = self.client.get(self.url, data={"username": "testtest123"})
        self.assertEqual(response.status_code, 200)


class EmailCheckTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("email_check_api")
        create_user()

    def test_invalid_data(self):
        response = self.client.get(self.url, data={"email000": "11@qq.com"})
        self.assertEqual(response.status_code, 200)

    def test_email_exists(self):
        response = self.client.get(self.url, data={"email": "test@qq.com"})
        self.assertEqual(response.status_code, 400)

    def test_email_does_not_exist(self):
        response = self.client.get(self.url, data={"email": "33testtest@qq.com"})
        self.assertEqual(response.status_code, 200)


class UserRegisterAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_register_api")
        set_captcha(self.client.session)

    def test_invalid_data(self):
        data = {"username": "test", "real_name": "TT"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_captcha(self):
        data = {"username": "test", "real_name": "TT", "password": "qqqqqq", "email": "6060@qq.com", "captcha": "bbaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"验证码错误"})

    def test_short_password(self):
        data = {"username": "test", "real_name": "TT", "password": "qq", "email": "6060@qq.com", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_same_username(self):
        create_user()
        data = {"username": "test", "real_name": "ww", "password": "zzzzzzz", "email": "606fds0@qq.com", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"用户名已存在"})

    def test_same_email(self):
        create_user(username="test1", email="test1@qq.com")
        data = {"username": "aa", "real_name": "ww", "password": "zzzzzzz", "email": "test1@qq.com", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该邮箱已被注册，请换其他邮箱进行注册"})

    def test_register_successfully(self):
        data = {"username": "cc", "real_name": "dd", "password": "xxxxxx", "email": "9090@qq.com", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"注册成功！"})


class UserChangePasswordAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_change_password_api")
        create_user()
        self.client.login(username="test",password="111111")
        set_captcha(self.client.session)

    def test_captcha(self):
        data = {"old_password": "aaaccc", "new_password": "aaaddd", "captcha": "abba"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"验证码错误"})

    def test_invalid_data(self):
        data = {"new_password": "aaaddd", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_error_old_password(self):
        data = {"old_password": "aaaccc", "new_password": "aaaddd", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"密码不正确，请重新修改！"})

    def test_change_password_successfully(self):
        data = {"old_password": "111111", "new_password": "aaaccc", "captcha": "aaaa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"用户密码修改成功！"})


class UserAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_admin_api")
        self.user = create_user(admin_type=SUPER_ADMIN)
        self.client.login(username="test", password="111111")

    def test_success_get_data(self):
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    def test_super_admin_required(self):
        create_user(username="test1", email="test1@qq.com", admin_type=ADMIN)
        self.client.login(username="test1", password="111111")

        self.assertEqual(json.loads(self.client.get(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest").content),
                         {"code": 1, "data": u"请先登录"})
        self.assertEqual(json.loads(self.client.put(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest").content),
                         {"code": 1, "data": u"请先登录"})

        # 这个拦截操作其实是 Middleware 完成的
        create_user(username="test2", email="test2@qq.com")
        self.client.login(username="test2", password="111111")
        self.assertEqual(json.loads(self.client.get(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest").content),
                         {"code": 1, "data": u"请先登录"})
        self.assertEqual(json.loads(self.client.put(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest").content),
                         {"code": 1, "data": u"请先登录"})

    def test_put_invalid_data(self):
        data = {"username": "test", "password": "testaa"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_user_does_not_exist(self):
        data = {"id": 8888, "username": "test0", "real_name": "test00",
                "password": "testaa", "email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该用户不存在！"})

    def test_username_exists(self):
        create_user(username="test1", email="test1@qq.com")
        data = {"id": self.user.id, "username": "test1", "real_name": "test00",
                "password": "testaa", "email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"昵称已经存在"})

    def test_edit_user_without_changing_password(self):
        data = {"id": self.user.id, "username": "test2", "real_name": "test00",
                "email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_user_edit_with_changing_password(self):
        data = {"id": self.user.id, "username": "test", "real_name": "test00", "password": "111111",
                "email": "60@qq.com", "admin_type": "2"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
        self.assertIsNotNone(auth.authenticate(username="test", password="111111"))

    def test_search_user(self):
        r = self.assertEqual(self.client.get(self.url + "?keyword=11").status_code, 200)

    def test_error_admin_type(self):
        response = self.client.get(self.url + "?admin_type=error")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})


class UserInfoAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user_info_api')
        self.user = create_user()

    def test_get_data_successfully(self):
        self.client.login(username="test", password="111111")
        data = self.client.get(self.url).data
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["username"], self.user.username)

    def test_get_data_without_logging_in(self):
        self.assertEqual(self.client.get(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest").data["code"], 1)


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
        self.assertRedirects(response, "/login/")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/login_required_test/fbv/1/")
        self.assertEqual(response.content, "function based view test1")

    def test_fbv_with_args(self):
        # 没登陆
        response = self.client.get("/login_required_test/fbv/1024/")
        self.assertRedirects(response, "/login/")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/login_required_test/fbv/1024/")
        self.assertEqual(response.content, "1024")

    def test_cbv_without_args(self):
        # 没登陆
        response = self.client.get("/login_required_test/cbv/1/")
        self.assertRedirects(response, "/login/")

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
        self.assertRedirects(response, "/login/")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/fbv/1/")
        self.assertEqual(response.content, "function based view test1")

    def test_fbv_with_args(self):
        # 没登陆
        response = self.client.get("/admin_required_test/fbv/1024/")
        self.assertRedirects(response, "/login/")

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/fbv/1024/")
        self.assertEqual(response.content, "1024")

    def test_cbv_without_args(self):
        # 没登陆
        response = self.client.get("/admin_required_test/cbv/1/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.data, {"code": 1, "data": u"请先登录"})

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/cbv/1/")
        self.assertEqual(response.content, "class based view login required test1")

    def test_cbv_with_args(self):
        # 没登陆
        response = self.client.get("/admin_required_test/cbv/1024/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.data, {"code": 1, "data": u"请先登录"})

        # 登陆后
        self.client.login(username="test", password="test")
        response = self.client.get("/admin_required_test/cbv/1024/")
        self.assertEqual(response.content, "1024")


@super_admin_required
def super_admin_required_FBV_test_without_args(request):
    return HttpResponse("function based view test1")


@super_admin_required
def super_admin_required_FBC_test_with_args(request, problem_id):
    return HttpResponse(problem_id)


class SuperAdminRequiredCBVTestWithoutArgs(APIView):
    @super_admin_required
    def get(self, request):
        return HttpResponse("class based view login required test1")


class SuperAdminRequiredCBVTestWithArgs(APIView):
    @super_admin_required
    def get(self, request, problem_id):
        return HttpResponse(problem_id)


class SuperAdminRequiredDecoratorTest(TestCase):
    urls = 'account.test_urls'

    def setUp(self):
        self.client = Client()
        create_user(admin_type=SUPER_ADMIN)

    def test_fbv_without_args(self):
        # 没登陆
        response = self.client.get("/super_admin_required_test/fbv/1/")
        self.assertRedirects(response, "/login/")

        # 登陆后
        self.client.login(username="test", password="111111")
        response = self.client.get("/super_admin_required_test/fbv/1/")
        self.assertEqual(response.content, "function based view test1")

    def test_fbv_with_args(self):
        # 没登陆
        response = self.client.get("/super_admin_required_test/fbv/1024/")
        self.assertRedirects(response, "/login/")

        # 登陆后
        self.client.login(username="test", password="111111")
        response = self.client.get("/super_admin_required_test/fbv/1024/")
        self.assertEqual(response.content, "1024")

    def test_cbv_without_args(self):
        # 没登陆
        response = self.client.get("/super_admin_required_test/cbv/1/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.data, {"code": 1, "data": u"请先登录"})

        # 登陆后
        self.client.login(username="test", password="111111")
        response = self.client.get("/super_admin_required_test/cbv/1/")
        self.assertEqual(response.content, "class based view login required test1")

    def test_cbv_with_args(self):
        # 没登陆
        response = self.client.get("/super_admin_required_test/cbv/1024/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.data, {"code": 1, "data": u"请先登录"})

        # 登陆后
        self.client.login(username="test", password="111111")
        response = self.client.get("/super_admin_required_test/cbv/10086/")
        self.assertEqual(response.content, "10086")


class UserLogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        create_user()

    def test_logout_success(self):
        self.client = Client()
        self.client.login(username="test", password="111111")
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)


class IndexPageTest(TestCase):
    def setUp(self):
        create_user()
        self.client = Client()

    def test_not_login_user(self):
        self.assertTemplateUsed(self.client.get("/"), "oj/index.html")

    def test_no_referer_redirect(self):
        self.client.login(username="test", password="111111")
        self.assertRedirects(self.client.get("/"), "/problems/")

    def test_visit_with_referer(self):
        self.client.login(username="test", password="111111")
        self.assertTemplateUsed(self.client.get("/", HTTP_REFERER="/about/"), "oj/index.html")
