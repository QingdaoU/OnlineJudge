# coding=utf-8
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIClient

from account.models import User


class AnnouncementAPITest(APITestCase):
        def setUp(self):
            self.client = APIClient()
            self.url = reverse("announcement_admin_api")
            user = User.objects.create(username="test")
            user.set_password("test")
            user.save()

        def test_invalid_format(self):
            self.client.login(username="test", password="test")
            data = {"title": "test1"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        def test_success_announcement(self):
            self.client.login(username="test", password="test")
            data = {"title": "title0", "content": "content0"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data, {"code": 0, "data": u"公告发布成功！"})