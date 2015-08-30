# coding=utf-8
import json

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIClient

from account.models import User, REGULAR_USER, ADMIN, SUPER_ADMIN
from group.models import Group, UserGroupRelation, JoinGroupRequest

from django.test import TestCase, Client


class GroupAPITest(APITestCase):
    pass


class GroupAdminAPITest(APITestCase):
    def _create_group(self, name, join_group_setting):
        group = Group.objects.create(name=name, description="des0",
                                     join_group_setting=join_group_setting, visible=True,
                                     admin=self.user)
        return group

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('group_admin_api')
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.group = self._create_group("group1", 0)
        self.client.login(username="test", password="testaa")

    # 以下是创建小组的测试
    def test_invalid_format(self):
        data = {"name": "group1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_create_group_successfully(self):
        data = {"name": "group0", "description": "des0", "join_group_setting": "1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_group_already_exists(self):
        data = {"name": "group1", "description": "des0", "join_group_setting": "1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组名已经存在"})

    # 以下是修改小组的测试
    def test_put_invalid_data(self):
        data = {"name": "group1"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_edit_group_does_not_exist(self):
        data = {"group_id": self.group.id + 1, "name": "group0", "description": "des0",
                "join_group_setting": 2}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组不存在"})

    def test_edit_group_successfully(self):
        data = {"group_id": self.group.id, "name": "group0", "description": "des0",
                "join_group_setting": 2}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"]["name"], "group0")
        self.assertEqual(response.data["data"]["join_group_setting"], 2)

    def test_edit_group_exists(self):
        group = self._create_group("group2", 1)
        data = {"group_id": group.id, "name": "group1", "description": "des0",
                "join_group_setting": 0}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组名已经存在"})

    # 以下是查询小组列表或者是单个小组时的测试
    def test_select_group_does_not_exist(self):
        data = {"group_id": self.group.id + 1}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组不存在"})

    def test_select_group_successfully(self):
        data = {"group_id": self.group.id}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def tests_get_all_groups_successfully(self):
        self.assertEqual(self.client.get(self.url).data["code"], 0)


class GroupMemberAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('group_member_admin_api')
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.user1 = User.objects.create(username="member1", admin_type=REGULAR_USER)
        self.user1.set_password("testxx")
        self.user1.save()
        self.client.login(username="test", password="testaa")
        self.group = Group.objects.create(name="group1", description="des1",
                                          join_group_setting="1", visible="True",
                                          admin=self.user)
        UserGroupRelation.objects.create(group=self.group, user=self.user1)

    # 以下是查询小组成员的测试
    def test_missing_parameter(self):
        self.assertEqual(self.client.get(self.url).data, {"code": 1, "data": u"参数错误"})

    def test_group_does_not_exist(self):
        data = {"group_id": self.group.id + 1}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组不存在"})

    def test_get_member_list_successfully(self):
        data = {"group_id": self.group.id}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    # 以下是删除小组成员的测试
    def test_invalid_format(self):
        data = {"members": [self.user1.id]}
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.data["code"], 1)

    def test_del_group_does_not_exist(self):
        data = {"group_id": self.group.id + 1, "members": [self.user1.id]}
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.data, {"code": 1, "data": u"小组不存在"})

    def test_del_members_successfully(self):
        data = {"group_id": self.group.id, "members": [self.user1.id]}
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.data, {"code": 0, "data": u"删除成功"})
        try:
            UserGroupRelation.objects.get(group=self.group, user=self.user1)
            raise AssertionError()
        except UserGroupRelation.DoesNotExist:
            pass


class JoinGroupAPITest(APITestCase):
    def _create_group(self, name, join_group_setting):
        group = Group.objects.create(name=name, description="des0",
                                     join_group_setting=join_group_setting, visible="True",
                                     admin=self.user)
        return group

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('group_join_admin_api')
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.client.login(username="test", password="testaa")
        self.group = self._create_group("group0", 0)

    # 以下是用户要加入某个小组的测试
    def test_invalid_format(self):
        data = {"message": "message1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_group_does_not_exist(self):
        data = {"group_id": self.group.id + 1, "message": "message1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"小组不存在"})

    def test_join0_successfully(self):
        data = {"group_id": self.group.id, "message": "message0"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"你已经成功的加入该小组"})

        # 再加入一遍  已经是小组成员了
        data = {"group_id": self.group.id, "message": "message0"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"你已经是小组成员了"})

    def test_join1_successfully(self):
        group = self._create_group("group1", 1)
        data = {"group_id": group.id, "message": "message1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"申请提交成功，请等待审核"})
        JoinGroupRequest.objects.get(user=self.user, group=group, status=False)

        # 再提交一遍 已经提交过申请，请等待审核
        data = {"group_id": group.id, "message": "message1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"你已经提交过申请了，请等待审核"})

    def test_join2_successfully(self):
        group = self._create_group("group2", 2)
        data = {"group_id": group.id, "message": "message2"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该小组不允许任何人加入"})

    # 以下是搜索小组的测试
    def test_error_get_data(self):
        self.assertEqual(self.client.get(self.url).data["code"], 1)

    def test_query_by_keyword(self):
        response = self.client.get(self.url + "?keyword=group0")
        self.assertEqual(response.data["code"], 0)


class JoinGroupRequestAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('join_group_request_admin_api')
        self.user = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.user1 = User.objects.create(username="test2")
        self.user1.set_password("testbb")
        self.user1.save()
        self.client.login(username="test1", password="testaa")
        self.group = Group.objects.create(name="group1", description="des0",
                                          join_group_setting=1, visible="True",
                                          admin=self.user)
        self.request = JoinGroupRequest.objects.create(group=self.group, user=self.user1,
                                                       message="message1")

    # 以下是管理的群的加群请求测试
    def test_get_all_request_successfully(self):
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    # 以下是同意或者拒绝加入小组请求的测试
    def test_invalid_format(self):
        data = {"requested_id": self.request.id}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_request_does_not_exist(self):
        data = {"request_id": self.request.id + 1, "status": False}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"请求不存在"})

    def test_request_refuse_successfully(self):
        data = {"request_id": self.request.id, "status": False}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"已拒绝"})
        self.assertEqual(JoinGroupRequest.objects.get(id=self.request.id).status, True)

    def test_join_group_successfully(self):
        data = {"request_id": self.request.id, "status": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 0, "data": u"加入成功"})
        UserGroupRelation.objects.get(group=self.group, user=self.user1)

        # 再加入一次，此时返回的消息应为 加入失败，已经在本小组内
        request = JoinGroupRequest.objects.create(group=self.group, user=self.user1,
                                                  message="message2")
        data = {"request_id": request.id, "status": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"加入失败，已经在本小组内"})


class ProblemListPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('group_list_page')
        self.url = reverse('problem_list_page', kwargs={"page": 1})
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.group = Group.objects.create(name="group1",
                                            description="description1",
                                            # 0是公开 1是需要申请后加入 2是不允许任何人加入
                                            join_group_setting = 1,
                                            admin=User.objects.get(username="test"))

    def get_group_list_page_successful(self):
        self.client.login(username="test", password="testaa")
        response = self.client.get(self.url)
        self.assertEqual(response.status_coed, 200)

    def get_group_list_page_successful_with_keyword(self):
        self.client.login(username="test", password="testaa")
        response = self.client.get(self.url+"?keyword=gro")
        self.assertEqual(response.status_coed, 200)

