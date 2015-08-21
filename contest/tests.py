# coding=utf-8
import json
from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework.test import APITestCase, APIClient

from account.models import User
from group.models import Group
from contest.models import Contest, ContestProblem
from announcement.models import Announcement
from account.models import REGULAR_USER, ADMIN, SUPER_ADMIN


class ContestAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contest_admin_api')
        user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        user1.set_password("testaa")
        user1.save()
        user2 = User.objects.create(username="test2", admin_type=ADMIN)
        user2.set_password("testbb")
        user2.save()
        user3 = User.objects.create(username="test3", admin_type=REGULAR_USER)
        user3.set_password("testcc")
        user3.save()
        self.group = Group.objects.create(name="group1", description="des0",
                                          join_group_setting=0, visible=True,
                                          admin=user2)
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=2, show_rank=True, show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))
        self.group_contest = Contest.objects.create(title="titley", description="descriptiony", mode=1,
                                                    contest_type=2, show_rank=True, show_user_submission=True,
                                                    start_time="2015-08-15T10:00:00.000Z",
                                                    end_time="2015-08-15T12:00:00.000Z",
                                                    password="aacc", created_by=User.objects.get(username="test1"))

    # 以下是比赛发布的测试
    def test_invalid_format(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "test1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_global_contest_does_not_has_privileges(self):
        self.client.login(username="test2", password="testbb")
        data = {"title": "title0", "description": "description0", "mode": 1, "contest_type": 2,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"只有超级管理员才可创建公开赛"})

    def test_global_contest_password_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title0", "description": "description0", "mode": 1, "contest_type": 2,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"此比赛为有密码的公开赛，密码不可为空"})

    def test_group_contest_group_at_least_one(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title0", "description": "description0", "mode": 1, "contest_type": 0,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"请至少选择一个小组"})

    def test_global_contest_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title1", "description": "description1", "mode": 1, "contest_type": 2,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_group_contest_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title3", "description": "description3", "mode": 1, "contest_type": 0,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "groups": [self.group.id], "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_time_error(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title2", "description": "description2", "mode": 1, "contest_type": 2,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T12:00:00.000Z",
                "end_time": "2015-08-15T10:00:00.000Z", "password": "aabb", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛的开始时间不能晚于或等于比赛结束的时间"})

    def test_contest_has_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "titlex", "description": "descriptionx", "mode": 1, "contest_type": 2,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛名已经存在"})

    # 以下是编辑比赛的测试
    def test_put_invalid_data(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "test0", "description": "description0"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_contest_does_not_exist(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id + 10, "title": "title2", "description": "description2", "mode": 1,
                "contest_type": 2, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该比赛不存在！"})

    def test_edit_global_contest_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "titlez", "description": "descriptionz", "mode": 1,
                "contest_type": 2, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T13:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"]["title"], "titlez")
        self.assertEqual(response.data["data"]["end_time"], "2015-08-15T13:00:00Z")

    def test_edit_group_contest_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.group_contest.id, "title": "titleyyy", "description": "descriptionyyyy", "mode": 1,
                "contest_type": 0, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T13:00:00.000Z",
                "groups": [self.group.id], "visible": False}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"]["title"], "titleyyy")
        self.assertEqual(response.data["data"]["end_time"], "2015-08-15T13:00:00Z")
        self.assertEqual(response.data["data"]["visible"], False)

    def test_edit_group_at_least_one(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.group_contest.id, "title": "titleyyy", "description": "descriptionyyyy", "mode": 1,
                "contest_type": 0, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T13:00:00.000Z", "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"请至少选择一个小组"})

    def test_edit_contest_has_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "titley", "description": "descriptiony", "mode": 1,
                "contest_type": 2, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该比赛名称已经存在"})

    def test_edit_global_contest_does_not_has_privileges(self):
        self.client.login(username="test2", password="testbb")
        data = {"id": self.global_contest.id, "title": "titlexxxxxxxxx", "description": "descriptionxxxxxx", "mode": 1,
                "contest_type": 2, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"只有超级管理员才可创建公开赛"})

    def test_edit_global_contest_password_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "title0", "description": "description0", "mode": 1, "contest_type": 2,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"此比赛为有密码的公开赛，密码不可为空"})

    def test_edit_time_error(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "titleaaaa", "description": "descriptionaaaaa", "mode": 1,
                "contest_type": 2, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T12:00:00.000Z", "end_time": "2015-08-15T10:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛的开始时间不能晚于或等于比赛结束的时间"})

    # 以下是比赛分页的测试
    def test_get_data_successfully(self):
        self.client.login(username="test1", password="testaa")
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    def test_keyword_contest(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?visible=true")
        self.assertEqual(response.data["code"], 0)
        for item in response.data["data"]:
            self.assertEqual(item["visible"], True)


class ContestProblemAdminAPItEST(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contest_problem_admin_api')
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.client.login(username="test", password="testaa")
        self. contest_problem = ContestProblem.objects.create(title="title1",
                                                              description="description1",
                                                              input_description="input1_description",
                                                              output_description="output1_description",
                                                              test_case_id="1",
                                                              samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                                              time_limit=100,
                                                              memory_limit=1000,
                                                              difficulty=1,
                                                              hint="hint1",
                                                              created_by=User.objects.get(username="test"),
                                                              sort_index="a")
