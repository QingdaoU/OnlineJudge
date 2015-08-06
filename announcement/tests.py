# coding=utf-8
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIClient

from account.models import User
from announcement.models import Announcement


class AnnouncementAdminAPITest(APITestCase):
        def setUp(self):
            self.client = APIClient()
            self.url = reverse("announcement_admin_api")
            user = User.objects.create(username="test")
            user.set_password("test")
            user.save()

        # 以下是发布公告的测试
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

        def test_post_invalid_data(self):
            self.client.login(username="test", password="test")
            data = {"title": "test"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        # 以下是编辑公告的测试
        def test_put_invalid_data(self):
            self.client.login(username="test", password="test")
            data = {"title": "test0", "content": "test0", "visible": "True"}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        def test_announcement_does_not_exist(self):
            announcement = Announcement.objects.create(title="aa",
                                                       content="AA",
                                                       created_by=User.objects.get(username="test"))
            data = {"id": announcement.id + 1, "title": "11", "content": "22", "visible": True}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data, {"code": 1, "data": u"该公告不存在！"})

        def test_success_edit_announcement(self):
            announcement = Announcement.objects.create(title="bb",
                                                       content="BB",
                                                       created_by=User.objects.get(username="test"))
            data = {"id": announcement.id, "title": "11", "content": "22", "visible": True}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data["code"], 0)


class AnnouncementAPITest(APITestCase):
        def setUp(self):
            self.client = APIClient()
            self.url = reverse("announcement_list_api")

        def test_success_get_data(self):
            self.assertEqual(self.client.get(self.url).data["code"], 0)
