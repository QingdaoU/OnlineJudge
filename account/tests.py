import time
from unittest import mock
from datetime import timedelta

from django.contrib import auth
from django.utils.timezone import now
from otpauth import OtpAuth

from utils.api.tests import APIClient, APITestCase
from utils.shortcuts import rand_str
from utils.cache import default_cache
from utils.constants import CacheKey

from .models import AdminType, ProblemPermission, User
from conf.models import WebsiteConfig


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


class DuplicateUserCheckAPITest(APITestCase):
    def setUp(self):
        self.create_user("test", "test123", login=False)
        self.url = self.reverse("check_username_or_email")

    def test_duplicate_username(self):
        resp = self.client.post(self.url, data={"username": "test"})
        data = resp.data["data"]
        self.assertEqual(data["username"], True)

    def test_ok_username(self):
        resp = self.client.post(self.url, data={"username": "test1"})
        data = resp.data["data"]
        self.assertEqual(data["username"], False)


class TFARequiredCheckAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("tfa_required_check")
        self.create_user("test", "test123", login=False)

    def test_not_required_tfa(self):
        resp = self.client.post(self.url, data={"username": "test"})
        self.assertSuccess(resp)
        self.assertEqual(resp.data["data"]["result"], False)

    def test_required_tfa(self):
        user = User.objects.first()
        user.two_factor_auth = True
        user.save()
        resp = self.client.post(self.url, data={"username": "test"})
        self.assertEqual(resp.data["data"]["result"], True)


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
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_login_with_wrong_info(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": "invalid_password"})
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid username or password"})

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
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_tfa_login_wrong_code(self):
        self._set_tfa()
        response = self.client.post(self.login_url,
                                    data={"username": self.username,
                                          "password": self.password,
                                          "tfa_code": "qqqqqq"})
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid two factor verification code"})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())

    def test_tfa_login_without_code(self):
        self._set_tfa()
        response = self.client.post(self.login_url,
                                    data={"username": self.username,
                                          "password": self.password})
        self.assertDictEqual(response.data, {"error": "error", "data": "tfa_required"})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())

    def test_user_disabled(self):
        self.user.is_disabled = True
        self.user.save()
        resp = self.client.post(self.login_url, data={"username": self.username,
                                                      "password": self.password})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Your account have been disabled"})


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
        # clea cache in redis
        default_cache.delete(CacheKey.website_config)

    def test_website_config_limit(self):
        website = WebsiteConfig.objects.create()
        website.allow_register = False
        website.save()
        resp = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Register have been disabled by admin"})

    def test_invalid_captcha(self):
        self.data["captcha"] = "****"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid captcha"})

        self.data.pop("captcha")
        response = self.client.post(self.register_url, data=self.data)
        self.assertTrue(response.data["error"] is not None)

    def test_register_with_correct_info(self):
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})

    def test_username_already_exists(self):
        self.test_register_with_correct_info()

        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["email"] = "test1@qduoj.com"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Username already exists"})

    def test_email_already_exists(self):
        self.test_register_with_correct_info()

        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["username"] = "test_user1"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Email already exists"})


class SessionManagementAPITest(APITestCase):
    def setUp(self):
        self.create_user("test", "test123")
        self.url = self.reverse("session_management_api")
        # launch a request to provide session data
        login_url = self.reverse("user_login_api")
        self.client.post(login_url, data={"username": "test", "password": "test123"})

    def test_get_sessions(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
        data = resp.data["data"]
        self.assertEqual(len(data), 1)

    # def test_delete_session_key(self):
    #     resp = self.client.delete(self.url + "?session_key=" + self.session_key)
    #     self.assertSuccess(resp)

    def test_delete_session_with_invalid_key(self):
        resp = self.client.delete(self.url + "?session_key=aaaaaaaaaa")
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid session_key"})


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("user_profile_api")

    def test_get_profile_without_login(self):
        resp = self.client.get(self.url)
        self.assertDictEqual(resp.data, {"error": None, "data": 0})

    def test_get_profile(self):
        self.create_user("test", "test123")
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_update_profile(self):
        self.create_user("test", "test123")
        update_data = {"real_name": "zemal", "submission_number": 233}
        resp = self.client.put(self.url, data=update_data)
        self.assertSuccess(resp)
        data = resp.data["data"]
        self.assertEqual(data["real_name"], "zemal")
        self.assertEqual(data["submission_number"], 0)


class TwoFactorAuthAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("two_factor_auth_api")
        self.create_user("test", "test123")
        self.create_website_config()

    def _get_tfa_code(self):
        user = User.objects.first()
        code = OtpAuth(user.tfa_token).totp()
        if len(str(code)) < 6:
            code = (6 - len(str(code))) * "0" + str(code)
        return code

    def test_get_image(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_open_tfa_with_invalid_code(self):
        self.test_get_image()
        resp = self.client.post(self.url, data={"code": "000000"})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid code"})

    def test_open_tfa_with_correct_code(self):
        self.test_get_image()
        code = self._get_tfa_code()
        resp = self.client.post(self.url, data={"code": code})
        self.assertSuccess(resp)
        user = User.objects.first()
        self.assertEqual(user.two_factor_auth, True)

    def test_close_tfa_with_invalid_code(self):
        self.test_open_tfa_with_correct_code()
        resp = self.client.post(self.url, data={"code": "000000"})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid code"})

    def test_close_tfa_with_correct_code(self):
        self.test_open_tfa_with_correct_code()
        code = self._get_tfa_code()
        resp = self.client.put(self.url, data={"code": code})
        self.assertSuccess(resp)
        user = User.objects.first()
        self.assertEqual(user.two_factor_auth, False)


@mock.patch("account.views.oj.send_email_async.delay")
class ApplyResetPasswordAPITest(CaptchaTest):
    def setUp(self):
        self.create_user("test", "test123", login=False)
        user = User.objects.first()
        user.email = "test@oj.com"
        user.save()
        self.url = self.reverse("apply_reset_password_api")
        self.create_website_config()
        self.data = {"email": "test@oj.com", "captcha": self._set_captcha(self.client.session)}

    def _refresh_captcha(self):
        self.data["captcha"] = self._set_captcha(self.client.session)

    def test_apply_reset_password(self, send_email_delay):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        send_email_delay.assert_called()

    def test_apply_reset_password_twice_in_20_mins(self, send_email_delay):
        self.test_apply_reset_password()
        send_email_delay.reset_mock()
        self._refresh_captcha()
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "You can only reset password once per 20 minutes"})
        send_email_delay.assert_not_called()

    def test_apply_reset_password_again_after_20_mins(self, send_email_delay):
        self.test_apply_reset_password()
        user = User.objects.first()
        user.reset_password_token_expire_time = now() - timedelta(minutes=21)
        user.save()
        self._refresh_captcha()
        self.test_apply_reset_password()


class ResetPasswordAPITest(CaptchaTest):
    def setUp(self):
        self.create_user("test", "test123", login=False)
        self.url = self.reverse("reset_password_api")
        user = User.objects.first()
        user.reset_password_token = "online_judge?"
        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        self.data = {"token": user.reset_password_token,
                     "captcha": self._set_captcha(self.client.session),
                     "password": "test456"}

    def test_reset_password_with_correct_token(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        self.assertTrue(self.client.login(username="test", password="test456"))

    def test_reset_password_with_invalid_token(self):
        self.data["token"] = "aaaaaaaaaaa"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Token dose not exist"})

    def test_reset_password_with_expired_token(self):
        user = User.objects.first()
        user.reset_password_token_expire_time = now() - timedelta(seconds=30)
        user.save()
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Token have expired"})


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
        self.assertEqual(response.data, {"error": "permission-denied", "data": "Please login in first"})

    def test_valid_ola_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": None, "data": "Succeeded"})
        self.assertTrue(self.client.login(username=self.username, password=self.new_password))

    def test_invalid_old_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        self.data["old_password"] = "invalid"
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": "error", "data": "Invalid old password"})


class AdminUserTest(APITestCase):
    def setUp(self):
        self.user = self.create_super_admin(login=True)
        self.username = self.password = "test"
        self.regular_user = self.create_user(username=self.username, password=self.password, login=False)
        self.url = self.reverse("user_admin_api")
        self.data = {"id": self.regular_user.id, "username": self.username, "real_name": "test_name",
                     "email": "test@qq.com", "admin_type": AdminType.REGULAR_USER,
                     "problem_permission": ProblemPermission.OWN, "open_api": True,
                     "two_factor_auth": False, "is_disabled": False}

    def test_user_list(self):
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_edit_user_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        self.assertEqual(resp_data["username"], self.username)
        self.assertEqual(resp_data["email"], "test@qq.com")
        self.assertEqual(resp_data["open_api"], True)
        self.assertEqual(resp_data["two_factor_auth"], False)
        self.assertEqual(resp_data["is_disabled"], False)
        self.assertEqual(resp_data["problem_permission"], ProblemPermission.NONE)

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


class UserRankAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("user_rank_api")
        self.create_user("test1", "test123", login=False)
        self.create_user("test2", "test123", login=False)
        test1 = User.objects.get(username="test1")
        profile1 = test1.userprofile
        profile1.submission_number = 10
        profile1.accepted_number = 10
        profile1.total_score = 240
        profile1.save()

        test2 = User.objects.get(username="test2")
        profile2 = test2.userprofile
        profile2.submission_number = 15
        profile2.accepted_number = 10
        profile2.total_score = 700
        profile2.save()

    def test_get_acm_rank(self):
        resp = self.client.get(self.url, data={"rule": "acm"})
        self.assertSuccess(resp)
        data = resp.data["data"]
        self.assertEqual(data[0]["user"]["username"], "test1")
        self.assertEqual(data[1]["user"]["username"], "test2")

    def test_get_oi_rank(self):
        resp = self.client.get(self.url, data={"rule": "oi"})
        self.assertSuccess(resp)
        data = resp.data["data"]
        self.assertEqual(data[0]["user"]["username"], "test2")
        self.assertEqual(data[1]["user"]["username"], "test1")
