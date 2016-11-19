import time
from unittest import mock

from django.contrib import auth
from django.utils.translation import ugettext as _

from utils.otp_auth import OtpAuth
from utils.shortcuts import rand_str
from utils.api.tests import APITestCase, APIClient

from .models import User, AdminType


class PermissionDecoratorTest(APITestCase):
    def setUp(self):
        self.regular_user = User.objects.create(username="regular_user")
        self.admin = User.objects.create(username="admin")
        self.super_admin = User.objects.create(username="super_admin")
        self.request = mock.MagicMock()
        self.request.user.is_authenticated = mock.MagicMock()

    def test_login_required(self):
        self.request.user.is_authenticated.return_value = False

    def test_admin_required(self):
        pass

    def test_super_admin_required(self):
        pass


class UserLoginAPITest(APITestCase):
    def setUp(self):
        self.username = self.password = "test"
        self.user = self.create_user(username=self.username, password=self.password, login=False)
        self.login_url = self.reverse("user_login_api")

    def _set_tfa(self):
        self.user.two_factor_auth = True
        tfa_token = rand_str(32)
        self.user.tfa_token = tfa_token
        self.user.save()
        return tfa_token

    def test_login_with_correct_info(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": self.password})
        self.assertDictEqual(response.data, {"error": None, "data": _("Succeeded")})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_login_with_wrong_info(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": "invalid_password"})
        self.assertDictEqual(response.data, {"error": "error", "data": _("Invalid username or password")})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())

    def test_tfa_login(self):
        token = self._set_tfa()
        code = OtpAuth(token).totp()
        if len(str(code)) < 6:
            code = (6 - len(str(code))) * "0" + str(code)
        response = self.client.post(self.login_url,
                                    data={"username": self.username,
                                          "password": self.password,
                                          "tfa_code": code})
        self.assertDictEqual(response.data, {"error": None, "data": _("Succeeded")})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_tfa_login_wrong_code(self):
        self._set_tfa()
        response = self.client.post(self.login_url,
                                    data={"username": self.username,
                                          "password": self.password,
                                          "tfa_code": "qqqqqq"})
        self.assertDictEqual(response.data, {"error": "error", "data": _("Invalid two factor verification code")})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())

    def test_tfa_login_without_code(self):
        self._set_tfa()
        response = self.client.post(self.login_url,
                                    data={"username": self.username,
                                          "password": self.password})
        self.assertDictEqual(response.data, {"error": None, "data": "tfa_required"})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())


class CaptchaTest(APITestCase):
    def _set_captcha(self, session):
        captcha = rand_str(4)
        session["_django_captcha_key"] = captcha
        session["_django_captcha_expires_time"] = int(time.time()) + 30
        session.save()
        return captcha


class UserRegisterAPITest(CaptchaTest):
    def setUp(self):
        self.client = APIClient()
        self.register_url = self.reverse("user_register_api")
        self.captcha = rand_str(4)

        self.data = {"username": "test_user", "password": "testuserpassword",
                     "real_name": "real_name", "email": "test@qduoj.com",
                     "captcha": self._set_captcha(self.client.session)}

    def test_invalid_captcha(self):
        self.data["captcha"] = "****"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": _("Invalid captcha")})

        self.data.pop("captcha")
        response = self.client.post(self.register_url, data=self.data)
        self.assertTrue(response.data["error"] is not None)

    def test_register_with_correct_info(self):
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": None, "data": _("Succeeded")})

    def test_username_already_exists(self):
        self.test_register_with_correct_info()

        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["email"] = "test1@qduoj.com"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": _("Username already exists")})

    def test_email_already_exists(self):
        self.test_register_with_correct_info()

        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["username"] = "test_user1"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": _("Email already exists")})


class UserChangePasswordAPITest(CaptchaTest):
    def setUp(self):
        self.client = APIClient()
        self.url = self.reverse("user_change_password_api")

        # Create user at first
        self.username = "test_user"
        self.old_password = "testuserpassword"
        self.new_password = "new_password"
        self.create_user(username=self.username, password=self.old_password, login=False)

        self.data = {"old_password": self.old_password, "new_password": self.new_password,
                     "captcha": self._set_captcha(self.client.session)}

    def test_login_required(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": "permission-denied", "data": _("Please login in first")})

    def test_valid_ola_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": None, "data": _("Succeeded")})
        self.assertTrue(self.client.login(username=self.username, password=self.new_password))

    def test_invalid_old_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        self.data["old_password"] = "invalid"
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": "error", "data": _("Invalid old password")})


class AdminUserTest(APITestCase):
    def setUp(self):
        self.user = self.create_super_admin(login=True)
        self.username = self.password = "test"
        self.regular_user = self.create_user(username=self.username, password=self.password, login=False)
        self.url = self.reverse("user_admin_api")
        self.data = {"id": self.regular_user.id, "username": self.username, "real_name": "test_name",
                     "email": "test@qq.com", "admin_type": AdminType.REGULAR_USER,
                     "open_api": True, "two_factor_auth": False, "is_disabled": False}

    def test_user_list(self):
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_edit_user_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        self.assertEqual(resp_data["username"], self.username)
        self.assertEqual(resp_data["email"], "test@qq.com")
        self.assertEqual(resp_data["real_name"], "test_name")
        self.assertEqual(resp_data["open_api"], True)
        self.assertEqual(resp_data["two_factor_auth"], False)
        self.assertEqual(resp_data["is_disabled"], False)

        self.assertTrue(self.regular_user.check_password("test"))

    def test_edit_user_password(self):
        data = self.data
        new_password = "testpassword"
        data["password"] = new_password
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        user = User.objects.get(id=self.regular_user.id)
        self.assertFalse(user.check_password(self.password))
        self.assertTrue(user.check_password(new_password))

    def test_edit_user_tfa(self):
        data = self.data
        self.assertIsNone(self.regular_user.tfa_token)
        data["two_factor_auth"] = True
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        # if `tfa_token` is None, a new value will be generated
        self.assertTrue(resp_data["two_factor_auth"])
        token = User.objects.get(id=self.regular_user.id).tfa_token
        self.assertIsNotNone(token)

        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        # if `tfa_token` is not None, the value is not changed
        self.assertTrue(resp_data["two_factor_auth"])
        self.assertEqual(User.objects.get(id=self.regular_user.id).tfa_token, token)

    def test_edit_user_openapi(self):
        data = self.data
        self.assertIsNone(self.regular_user.open_api_appkey)
        data["open_api"] = True
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        # if `open_api_appkey` is None, a new value will be generated
        self.assertTrue(resp_data["open_api"])
        key = User.objects.get(id=self.regular_user.id).open_api_appkey
        self.assertIsNotNone(key)

        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        # if `openapi_app_key` is not None, the value is not changed
        self.assertTrue(resp_data["open_api"])
        self.assertEqual(User.objects.get(id=self.regular_user.id).open_api_appkey, key)
