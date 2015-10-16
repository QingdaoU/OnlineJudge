# coding=utf-8
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient

from account.models import User
from account.tests import create_user
from group.models import Group
from announcement.models import Announcement
from account.models import ADMIN, SUPER_ADMIN


class AnnouncementAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("announcement_admin_api")
        self.user1 = create_user(admin_type=SUPER_ADMIN)

        self.user2 = create_user(username="test1", email="test1@qq.com", admin_type=SUPER_ADMIN)

        self.announcement = Announcement.objects.create(title="bb",
                                                        content="BB",
                                                        created_by=self.user1)

    def test_create_announcement_successfully(self):
        self.client.login(username="test", password="111111")
        data = {"title": "title0", "content": "content0"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"公告发布成功！"})

    def test_edit_announcement_successfully(self):
        self.client.login(username="test", password="111111")
        data = {"id": self.announcement.id, "title": "11", "content": "22", "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)


class AnnouncementPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        user = create_user()
        self.a1 = Announcement.objects.create(title="aa",
                                              content="AA",
                                              created_by=user,
                                              visible=True,
                                              )

        self.a2 = Announcement.objects.create(title="bb",
                                              content="BB",
                                              created_by=User.objects.get(username="test"),
                                              visible=False
                                              )

    def test_visit_announcement_successfully(self):
        response = self.client.get('/announcement/' + str(self.a1.id) + "/")
        self.assertTemplateUsed(response, "oj/announcement/announcement.html")

    def test_announcement_does_not_exist(self):
        response = self.client.get('/announcement/10086/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_visit_hidden_announcement(self):
        response = self.client.get('/announcement/' + str(self.a2.id) + "/")
        self.assertTemplateUsed(response, "utils/error.html")
