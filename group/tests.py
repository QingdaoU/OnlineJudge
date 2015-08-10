# coding=utf-8
from django.test import TestCase

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIClient

from account.models import User, SUPER_ADMIN
from group.models import Group


class GroupAdminAPITest(APITestCase):
    # 以下是创建小组的测试
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('group_admin_api')
        user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        user.set_password("testaa")
        user.save()

    def test_invalid_format(self):
        self.client.login(username="test", password="testaa")
        data = {"name": "group1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_success_group(self):
        self.client.login(username="test", password="testaa")
        data = {"name": "group1", "description": "des1", "join_group_setting": "1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    # 以下是修改小组的测试
    def test_put_invalid_data(self):
        self.client.login(username="test", password="testaa")
        data = {"name": "group1"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_edit_group_does_not_exist(self):
        self.client.login(username="test", password="testaa")
        group = Group.objects.create(name="group1", description="des1",
                                     join_group_setting="1", visible="True",
                                     admin=User.objects.get(username="test"))
        data = {"group_id": group.id + 1, "name": "group0", "description": "des0",
                "join_group_setting": 2}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组不存在"})

    def test_success_edit_group(self):
        self.client.login(username="test", password="testaa")
        group = Group.objects.create(name="group1", description="des1",
                                     join_group_setting="1", visible="True",
                                     admin=User.objects.get(username="test"))
        data = {"group_id": group.id, "name": "group0", "description": "des0",
                "join_group_setting": 2}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    # 以下是查询小组列表或者是单个小组时的测试
    def test_select_group_does_not_exist(self):
        self.client.login(username="test", password="testaa")
        group = Group.objects.create(name="group1", description="des1",
                                     join_group_setting="1", visible="True",
                                     admin=User.objects.get(username="test"))
        data = {"group_id": group.id + 1, "name": "group0", "description": "des0",
                "join_group_setting": 2}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组不存在"})

    def test_success_select_group(self):
        self.client.login(username="test", password="testaa")
        group = Group.objects.create(name="group1", description="des1",
                                     join_group_setting="1", visible="True",
                                     admin=User.objects.get(username="test"))
        data = {"group_id": group.id, "name": "group0", "description": "des0",
                "join_group_setting": 2}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_success_get_data(self):
        self.client.login(username="test", password="testaa")
        self.assertEqual(self.client.get(self.url).data["code"], 0)


