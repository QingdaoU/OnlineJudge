# coding=utf-8
from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework.test import APITestCase, APIClient

from account.models import User
from group.models import Group
from announcement.models import Announcement
from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN


class AnnouncementAdminAPITest(APITestCase):
        def setUp(self):
            self.client = APIClient()
            self.url = reverse("announcement_admin_api")
            user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
            user1.set_password("testaa")
            user1.save()
            user2 = User.objects.create(username="test2", admin_type=ADMIN)
            user2.set_password("testbb")
            user2.save()
            self.group = Group.objects.create(name="group1", description="des0",
                                              join_group_setting=0, visible=True,
                                              admin=user2)
            self.announcement = Announcement.objects.create(title="bb",
                                                            content="BB",
                                                            created_by=User.objects.get(username="test2"),
                                                            is_global=False)

        # 以下是发布公告的测试
        def test_invalid_format(self):
            self.client.login(username="test1", password="testaa")
            data = {"title": "test1"}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        def test_group_at_least_one(self):
            self.client.login(username="test1", password="testaa")
            data = {"title": "title0", "content": "content0", "is_global": False}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data, {"code": 1, "data": u"至少选择一个小组"})

        def test_global_announcement_successfully(self):
            self.client.login(username="test1", password="testaa")
            data = {"title": "title0", "content": "content0", "is_global": True}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data, {"code": 0, "data": u"公告发布成功！"})

        def test_group_announcement_successfully(self):
            self.client.login(username="test2", password="testbb")
            data = {"title": "title0", "content": "content0", "is_global": False, "groups": [self.group.id]}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data, {"code": 0, "data": u"公告发布成功！"})

        def test_global_announcement_does_not_has_privileges(self):
            self.client.login(username="test2", password="testbb")
            data = {"title": "title0", "content": "content0", "is_global": True}
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.data, {"code": 1, "data": u"只有超级管理员可以创建全局公告"})

        # 以下是编辑公告的测试
        def test_put_invalid_data(self):
            self.client.login(username="test1", password="testaa")
            data = {"title": "test0", "content": "test0", "visible": "True"}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data["code"], 1)

        def test_announcement_does_not_exist(self):
            self.client.login(username="test1", password="testaa")
            announcement = Announcement.objects.create(title="aa",
                                                       content="AA",
                                                       created_by=User.objects.get(username="test1"),
                                                       is_global=True)
            data = {"id": announcement.id + 1, "title": "11", "content": "22",
                    "visible": True, "is_global": True}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data, {"code": 1, "data": u"公告不存在"})

        def test_edit_global_announcement_successfully(self):
            self.client.login(username="test1", password="testaa")
            data = {"id": self.announcement.id, "title": "11", "content": "22",
                    "visible": True, "is_global": True}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data["code"], 0)

        def test_edit_group_announcement_successfully(self):
            self.client.login(username="test2", password="testbb")
            data = {"id": self.announcement.id, "title": "11", "content": "22",
                    "visible": True, "is_global": False, "groups": [self.group.id]}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data["code"], 0)
            self.assertEqual(response.data["data"]["title"], "11")
            self.assertEqual(response.data["data"]["content"], "22")

        def test_edit_group_at_least_one(self):
            self.client.login(username="test1", password="testaa")
            data = {"id": self.announcement.id, "title": "title0", "content": "content0",
                    "visible": True, "is_global": False}
            response = self.client.put(self.url, data=data)
            self.assertEqual(response.data, {"code": 1, "data": u"至少选择一个小组"})

        # 以下是公告分页的测试
        def test_get_data_successfully(self):
            self.client.login(username="test1", password="testaa")
            self.assertEqual(self.client.get(self.url).data["code"], 0)

        def test_keyword_global_announcement(self):
            self.client.login(username="test1", password="testaa")
            Announcement.objects.create(title="aa",
                                        content="AA",
                                        created_by=User.objects.get(username="test1"),
                                        visible=True,
                                        is_global=True)

            Announcement.objects.create(title="bb",
                                        content="BB",
                                        created_by=User.objects.get(username="test1"),
                                        visible=False,
                                        is_global=True)

            response = self.client.get(self.url + "?visible=true")
            self.assertEqual(response.data["code"], 0)
            for item in response.data["data"]:
                self.assertEqual(item["visible"], True)

        def test_keyword_group_announcement(self):
            self.client.login(username="test2", password="testbb")
            Announcement.objects.create(title="aa",
                                        content="AA",
                                        created_by=User.objects.get(username="test2"),
                                        visible=True,
                                        is_global=False)

            Announcement.objects.create(title="cc",
                                        content="CC",
                                        created_by=User.objects.get(username="test2"),
                                        visible=False,
                                        is_global=False)

            response = self.client.get(self.url + "?visible=true")
            self.assertEqual(response.data["code"], 0)
            for item in response.data["data"]:
                self.assertEqual(item["visible"], True)


class AnnouncementPageTest(TestCase):
    def setUp(self):
        user = User.objects.create(username="test")
        user.set_password("testaa")
        user.save()
        Announcement.objects.create(title="aa",
                                    content="AA",
                                    created_by=User.objects.get(username="test"),
                                    visible=True,
                                    is_global=True)

        Announcement.objects.create(title="bb",
                                    content="BB",
                                    created_by=User.objects.get(username="test"),
                                    visible=False,
                                    is_global=True)

    def test_visit_announcement_successfully(self):
        response = self.client.get('/announcement/1/')
        self.assertEqual(response.status_code, 200)

    def test_announcement_does_not_exist(self):
        response = self.client.get('/announcement/3/')
        self.assertTemplateUsed(response, "utils/error.html")

