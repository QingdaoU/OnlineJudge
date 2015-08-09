# coding=utf-8
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIClient

from account.models import User
from announcement.models import Announcement
from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN


class AnnouncementAdminAPITest(APITestCase):
        def setUp(self):
            self.client = APIClient()
            self.url = reverse("announcement_admin_api")
            user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
            user.set_password("testaa")
            user.save()

        # 以下是发布公告的测试
        def test_invalid_format(self):
            self.client.login(username="test", password="testaa")
            data = {"title": "test1"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        def test_success_announcement(self):
            self.client.login(username="test", password="testaa")
            data = {"title": "title0", "content": "content0"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data, {"code": 0, "data": u"公告发布成功！"})

        def test_post_invalid_data(self):
            self.client.login(username="test", password="testaa")
            data = {"title": "test"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        # 以下是编辑公告的测试
        def test_put_invalid_data(self):
            self.client.login(username="test", password="testaa")
            data = {"title": "test0", "content": "test0", "visible": "True"}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        def test_announcement_does_not_exist(self):
            self.client.login(username="test", password="testaa")
            announcement = Announcement.objects.create(title="aa",
                                                       content="AA",
                                                       created_by=User.objects.get(username="test"))
            data = {"id": announcement.id + 1, "title": "11", "content": "22", "visible": True}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data, {"code": 1, "data": u"该公告不存在！"})

        def test_success_edit_announcement(self):
            self.client.login(username="test", password="testaa")
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
            user = User.objects.create(username="test")
            user.set_password("testaa")
            user.save()

        def test_success_get_data(self):
            self.assertEqual(self.client.get(self.url).data["code"], 0)

        def test_keyword_announcement(self):
            Announcement.objects.create(title="aa",
                                        content="AA",
                                        created_by=User.objects.get(username="test"),
                                        visible=True)

            Announcement.objects.create(title="bb",
                                        content="BB",
                                        created_by=User.objects.get(username="test"),
                                        visible=False)

            response = self.client.get(self.url + "?visible=true")
            self.assertEqual(response.data["code"], 0)
            for item in response.data["data"]:
                self.assertEqual(item["visible"], True)
