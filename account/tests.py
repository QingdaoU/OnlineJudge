# coding=utf-8
from __future__ import unicode_literals
import time
import mock

from django.contrib import auth
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from rest_framework.test import APIClient, APITestCase

from utils.shortcuts import rand_str
from utils.otp_auth import OtpAuth
from .models import User


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
        self.username = "testuser"
        self.password = "testuserpassword"
        self.user = User.objects.create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.login_url = reverse("user_login_api")

    def _set_tfa(self):
        self.user.two_factor_auth = True
        tfa_token = rand_str(32)
        self.user.tfa_token = tfa_token
        self.user.save()
        return tfa_token

    def test_login_with_correct_info(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": self.password})
        self.assertDictEqual(response.data, {"code": 0, "data": _("Succeeded")})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_login_with_wrong_info(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": "invalid_password"})

        self.assertDictEqual(response.data, {"code": 1, "data": _("Invalid username or password")})

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
        self.assertDictEqual(response.data, {"code": 0, "data": _("Succeeded")})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_tfa_login_wrong_code(self):
        self._set_tfa()
        response = self.client.post(self.login_url,
                                    data={"username": self.username,
                                          "password": self.password,
                                          "tfa_code": "qqqqqq"})
        self.assertDictEqual(response.data, {"code": 1, "data": _("Invalid two factor verification code")})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())

    def test_tfa_login_without_code(self):
        self._set_tfa()
        response = self.client.post(self.login_url,
                                    data={"username": self.username,
                                          "password": self.password})
        self.assertDictEqual(response.data, {"code": 0, "data": "tfa_required"})

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
        self.register_url = reverse("user_register_api")
        self.captcha = rand_str(4)

        self.data = {"username": "test_user", "password": "testuserpassword",
                     "real_name": "real_name", "email": "test@qduoj.com",
                     "captcha": self._set_captcha(self.client.session)}

    def test_invalid_captcha(self):
        self.data["captcha"] = "****"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"code": 1, "data": _("Invalid captcha")})

        self.data.pop("captcha")
        response = self.client.post(self.register_url, data=self.data)
        self.assertEqual(response.data["code"], 1)

    def test_register_with_correct_info(self):
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"code": 0, "data": _("Succeeded")})

    def test_username_already_exists(self):
        self.test_register_with_correct_info()

        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["email"] = "test1@qduoj.com"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"code": 1, "data": _("Username already exists")})

    def test_email_already_exists(self):
        self.test_register_with_correct_info()

        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["username"] = "test_user1"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"code": 1, "data": _("Email already exists")})


class UserChangePasswordAPITest(CaptchaTest):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user_change_password_api")

        # Create user at first
        self.username = "test_user"
        self.old_password = "testuserpassword"
        self.new_password = "new_password"
        register_data = {"username": self.username, "password": self.old_password,
                         "real_name": "real_name", "email": "test@qduoj.com",
                         "captcha": self._set_captcha(self.client.session)}

        response = self.client.post(reverse("user_register_api"), data=register_data)
        self.assertDictEqual(response.data, {"code": 0, "data": _("Succeeded")})

        self.data = {"old_password": self.old_password, "new_password": self.new_password,
                     "captcha": self._set_captcha(self.client.session)}

    def test_login_required(self):
        response = self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.data, {"code": 1, "data": _("Please login in first")})

    def test_valid_ola_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        response = self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.data, {"code": 0, "data": _("Succeeded")})
        self.assertTrue(self.client.login(username=self.username, password=self.new_password))

    def test_invalid_old_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        self.data["old_password"] = "invalid"
        response = self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.data, {"code": 1, "data": _("Invalid old password")})


class AdminEditUserTest(APITestCase):
    def setUp(self):
        pass

    def test_edit_user_successfully(self):
        pass

    def test_change_user_admin_type(self):
        pass

    def test_change_user_permission(self):
        pass

    def test_change_user_password(self):
        pass
