from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from rest_framework.test import APIClient

from account.models import AdminType, User


class APITestCase(TestCase):
    client_class = APIClient

    def create_user(self, username, password, admin_type=AdminType.REGULAR_USER, login=True):
        user = User.objects.create(username=username, admin_type=admin_type)
        user.set_password(password)
        user.save()
        if login:
            self.client.login(username=username, password=password)
        return user

    def create_admin(self, username="admin", password="admin", login=True):
        return self.create_user(username=username, password=password, admin_type=AdminType.ADMIN, login=login)

    def create_super_admin(self, username="root", password="root", login=True):
        return self.create_user(username=username, password=password, admin_type=AdminType.SUPER_ADMIN, login=login)

    def reverse(self, url_name):
        return reverse(url_name)

    def assertSuccess(self, response):
        self.assertTrue(response.data["error"] is None)

    def assertFailed(self, response):
        self.assertTrue(response.data["error"] is not None)
