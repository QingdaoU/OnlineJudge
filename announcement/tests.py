# coding=utf-8
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIClient


class AnnouncementAPITest(APITestCase):
        def setUp(self):
            self.client = APIClient()
            self.url = reverse("announcement_api")

        def test_invalid_format(self):
            # todo 判断用户是否登录
            data = {"title": "test1"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data["code"], 1)
