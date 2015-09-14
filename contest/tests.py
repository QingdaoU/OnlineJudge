# coding=utf-8
import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient

from account.models import User
from group.models import Group
from contest.models import Contest, ContestProblem
from .models import ContestSubmission
from .models import GROUP_CONTEST, PASSWORD_PROTECTED_CONTEST
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
        self.group2 = Group.objects.create(name="group2", description="des0",
                                           join_group_setting=0, visible=True,
                                           admin=user1)
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))
        self.group_contest = Contest.objects.create(title="titley", description="descriptiony", mode=1,
                                                    contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                    show_user_submission=True,
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
        data = {"title": "title0", "description": "description0", "mode": 1, "contest_type": PASSWORD_PROTECTED_CONTEST,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"只有超级管理员才可创建公开赛"})

    def test_global_contest_password_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title0", "description": "description0", "mode": 1, "contest_type": PASSWORD_PROTECTED_CONTEST,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"此比赛为有密码的公开赛，密码不可为空"})

    def test_group_contest_group_at_least_one(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title0", "description": "description0", "mode": 1, "contest_type": GROUP_CONTEST,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"请至少选择一个小组"})

    def test_global_contest_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title1", "description": "description1", "mode": 1, "contest_type": PASSWORD_PROTECTED_CONTEST,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_group_contest_super_admin_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title3", "description": "description3", "mode": 1, "contest_type": GROUP_CONTEST,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "groups": [self.group.id], "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_group_contest_admin_successfully(self):
        self.client.login(username="test2", password="testbb")
        data = {"title": "title6", "description": "description6", "mode": 2, "contest_type": GROUP_CONTEST,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "groups": [self.group.id], "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_time_error(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "title2", "description": "description2", "mode": 1, "contest_type": PASSWORD_PROTECTED_CONTEST,
                "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T12:00:00.000Z",
                "end_time": "2015-08-15T10:00:00.000Z", "password": "aabb", "visible": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛的开始时间不能晚于或等于比赛结束的时间"})

    def test_contest_has_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"title": "titlex", "description": "descriptionx", "mode": 1, "contest_type": PASSWORD_PROTECTED_CONTEST,
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
                "contest_type": PASSWORD_PROTECTED_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该比赛不存在！"})

    def test_edit_global_contest_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "titlez", "description": "descriptionz", "mode": 1,
                "contest_type": PASSWORD_PROTECTED_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T13:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"]["title"], "titlez")
        #self.assertEqual(response.data["data"]["end_time"], "2015-08-15T13:00:00Z")

    def test_edit_group_contest_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.group_contest.id, "title": "titleyyy", "description": "descriptionyyyy", "mode": 1,
                "contest_type": GROUP_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T13:00:00.000Z",
                "groups": [self.group.id], "visible": False}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"]["title"], "titleyyy")
        #self.assertEqual(response.data["data"]["end_time"], "2015-08-15T13:00:00Z")
        self.assertEqual(response.data["data"]["visible"], False)

    def test_edit_group_contest_unsuccessfully(self):
        self.client.login(username="test2", password="testbb")
        data = {"id": self.group_contest.id, "title": "titleyyy", "description": "descriptionyyyy", "mode": 1,
                "contest_type": GROUP_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T13:00:00.000Z",
                "groups": [self.group.id], "visible": False}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_edit_group_at_least_one(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.group_contest.id, "title": "titleyyy", "description": "descriptionyyyy", "mode": 1,
                "contest_type": GROUP_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T13:00:00.000Z", "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"请至少选择一个小组"})

    def test_edit_contest_has_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "titley", "description": "descriptiony", "mode": 1,
                "contest_type": PASSWORD_PROTECTED_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该比赛名称已经存在"})

    def test_edit_global_contest_does_not_has_privileges(self):
        self.client.login(username="test2", password="testbb")
        data = {"id": self.global_contest.id, "title": "titlexxxxxxxxx", "description": "descriptionxxxxxx", "mode": 1,
                "contest_type": PASSWORD_PROTECTED_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T10:00:00.000Z", "end_time": "2015-08-15T12:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"只有超级管理员才可创建公开赛"})

    def test_edit_global_contest_password_exists(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "title0", "description": "description0", "mode": 1,
                "contest_type": PASSWORD_PROTECTED_CONTEST, "show_rank": True, "show_user_submission": True, "start_time": "2015-08-15T10:00:00.000Z",
                "end_time": "2015-08-15T12:00:00.000Z", "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"此比赛为有密码的公开赛，密码不可为空"})

    def test_edit_time_error(self):
        self.client.login(username="test1", password="testaa")
        data = {"id": self.global_contest.id, "title": "titleaaaa", "description": "descriptionaaaaa", "mode": 1,
                "contest_type": PASSWORD_PROTECTED_CONTEST, "show_rank": True, "show_user_submission": True,
                "start_time": "2015-08-15T12:00:00.000Z", "end_time": "2015-08-15T10:00:00.000Z", "password": "aabb",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛的开始时间不能晚于或等于比赛结束的时间"})

    # 以下是比赛分页的测试
    def test_get_data_successfully(self):
        self.client.login(username="test1", password="testaa")
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    def test_get_data_successfully_by_normal_admin(self):
        self.client.login(username="test2", password="testbb")
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    def test_keyword_contest(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?visible=true")
        self.assertEqual(response.data["code"], 0)
        for item in response.data["data"]:
            self.assertEqual(item["visible"], True)

    def test_query_by_keyword(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?keyword=title1")
        self.assertEqual(response.data["code"], 0)


class ContestProblemAdminAPItEST(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contest_problem_admin_api')
        self.user = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.user2 = User.objects.create(username="test2", admin_type=ADMIN)
        self.user2.set_password("testaa")
        self.user2.save()
        self.user3 = User.objects.create(username="test3", admin_type=ADMIN)
        self.user3.set_password("testaa")
        self.user3.save()
        self.client.login(username="test1", password="testaa")
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))
        self.contest_problem = ContestProblem.objects.create(title="titlex",
                                                             description="descriptionx",
                                                             input_description="input1_description",
                                                             output_description="output1_description",
                                                             test_case_id="1",
                                                             samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                                             time_limit=100,
                                                             memory_limit=1000,
                                                             hint="hint1",
                                                             created_by=User.objects.get(username="test1"),
                                                             contest=Contest.objects.get(title="titlex"),
                                                             sort_index="a")

    # 以下是发布比赛题目的测试
    def test_invalid_format(self):
        data = {"title": "test1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_release_contest_problem_successfully(self):
        data = {"title": "title2",
                "description": "description2",
                "input_description": "input_description2",
                "output_description": "output_description2",
                "test_case_id": "1",
                "source": "source1",
                "samples": [{"input": "1 1", "output": "2"}],
                "time_limit": "100",
                "memory_limit": "1000",
                "hint": "hint1",
                "sort_index": "b",
                "contest_id": self.global_contest.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_contest_does_not_exists(self):
        data = {"title": "titlezzzzzzzz",
                "description": "descriptionzzzzzzzzzzz",
                "input_description": "input_description2",
                "output_description": "output_description2",
                "test_case_id": "1",
                "source": "source1",
                "samples": [{"input": "1 1", "output": "2"}],
                "time_limit": "100",
                "memory_limit": "1000",
                "hint": "hint1",
                "sort_index": "b",
                "contest_id": self.global_contest.id + 10}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛不存在"})

    # 以下是编辑比赛题目的测试
    def test_invalid_data(self):
        data = {"title": "test1"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_edit_problem_does_not_exist(self):
        data = {"id": self.contest_problem.id + 1,
                "title": "title2",
                "description": "description2",
                "input_description": "input_description2",
                "output_description": "output_description2",
                "test_case_id": "1",
                "source": "source1",
                "samples": [{"input": "1 1", "output": "2"}],
                "time_limit": "100",
                "memory_limit": "1000",
                "hint": "hint1",
                "sort_index": "b",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该比赛题目不存在！"})

    def test_edit_problem_successfully(self):
        data = {"id": self.contest_problem.id,
                "title": "title2222222",
                "description": "description22222222",
                "input_description": "input_description2",
                "output_description": "output_description2",
                "test_case_id": "1",
                "source": "source1",
                "samples": [{"input": "1 1", "output": "2"}],
                "time_limit": "100",
                "memory_limit": "1000",
                "hint": "hint1",
                "sort_index": "b",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    # 以下是比赛题目分页的测试
    def test_get_data_successfully(self):
        self.client.login(username="test1", password="testaa")
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    def test_get_data_unsuccessfully(self):
        self.client.login(username="test1", password="testaa")
        self.assertEqual(self.client.get(self.url+"?contest_id=12").data["code"], 1)

    def test_keyword_contest(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?visible=true")
        self.assertEqual(response.data["code"], 0)
        for item in response.data["data"]:
            self.assertEqual(item["visible"], True)

    def test_query_by_keyword(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?keyword=title1")
        self.assertEqual(response.data["code"], 0)

    def test_query_contest_problem_does_not_exist(self):
        data = {"contest_problem_id": 1000000}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛题目不存在"})

    def test_query_contest_problem_exists(self):
        data = {"contest_problem_id": self.contest_problem.id}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_query_contest_problem_exists_by_contest_id(self):
        self.client.login(username="test3", password="testaa")
        response = self.client.get(self.url + "?contest_id=" + str(self.global_contest.id))
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(len(response.data["data"]), 0)

    def test_query_contest_problem_exists_by_normal_admin(self):
        self.client.login(username="test2", password="testaa")
        data = {"contest_problem_id": self.contest_problem.id}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_edit_problem_unsuccessfully_can_not_access(self):
        self.client.login(username="test2", password="testaa")
        data = {"id": self.contest_problem.id,
                "title": "title2222222",
                "description": "description22222222",
                "input_description": "input_description2",
                "output_description": "output_description2",
                "test_case_id": "1",
                "source": "source1",
                "samples": [{"input": "1 1", "output": "2"}],
                "time_limit": "100",
                "memory_limit": "1000",
                "hint": "hint1",
                "sort_index": "b",
                "visible": True}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)


class ContestPasswordVerifyAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contest_password_verify_api')
        self.user = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.user2 = User.objects.create(username="test2", admin_type=ADMIN)
        self.user2.set_password("testbb")
        self.user2.save()
        self.client.login(username="test1", password="testaa")
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))

    def test_invalid_format(self):
        self.client.login(username="test2", password="testbb")
        data = {"contest_id": self.global_contest.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_contest_does_not_exist(self):
        self.client.login(username="test2", password="testbb")
        data = {"contest_id": self.global_contest.id + 1, "password": "aacc"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"比赛不存在"})

    def test_contest_password_verify_unsuccessfully(self):
        self.client.login(username="test2", password="testbb")
        data = {"contest_id": self.global_contest.id, "password": "aabb"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"密码错误"})

    def test_contest_password_verify_successfully(self):
        self.client.login(username="test2", password="testbb")
        data = {"contest_id": self.global_contest.id, "password": "aacc"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)


class ContestPageTest(TestCase):
    # 单个比赛详情页的测试
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user1.set_password("testaa")
        self.user1.save()
        self.client.login(username="test1", password="testaa")
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))

    def test_visit_contest_page_successfully(self):
        response = self.client.get('/contest/1/')
        self.assertEqual(response.status_code, 200)

    def test_visit_contest_page_unsuccessfully(self):
        response = self.client.get('/contest/10/')
        self.assertTemplateUsed(response, "utils/error.html")


class ContestProblemPageTest(TestCase):
    # 单个比赛题目详情页的测试
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user1.set_password("testaa")
        self.user1.save()
        self.client.login(username="test1", password="testaa")
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))
        self.contest_problem = ContestProblem.objects.create(title="titlex",
                                                             description="descriptionx",
                                                             input_description="input1_description",
                                                             output_description="output1_description",
                                                             test_case_id="1",
                                                             samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                                             time_limit=100,
                                                             memory_limit=1000,
                                                             hint="hint1",
                                                             created_by=User.objects.get(username="test1"),
                                                             contest=Contest.objects.get(title="titlex"),
                                                             sort_index="a")

    def test_visit_contest_problem_page_successfully(self):
        response = self.client.get('/contest/1/problem/1/')
        self.assertEqual(response.status_code, 200)

    def test_visit_contest_page_unsuccessfully(self):
        response = self.client.get('/contest/10/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_visit_contest_submissions_page_successfully(self):
        ContestSubmission.objects.create(user=self.user1,
                                         contest=self.global_contest,
                                         problem=self.contest_problem,
                                         ac=True)
        response = self.client.get('/contest/1/problem/1/submissions/')
        self.assertEqual(response.status_code, 200)


class ContestProblemListPageTest(TestCase):
    # 比赛题目列表的测试
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user1.set_password("testaa")
        self.user1.save()
        self.client.login(username="test1", password="testaa")
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))
        self.contest_problem = ContestProblem.objects.create(title="titlex",
                                                             description="descriptionx",
                                                             input_description="input1_description",
                                                             output_description="output1_description",
                                                             test_case_id="1",
                                                             samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                                             time_limit=100,
                                                             memory_limit=1000,
                                                             hint="hint1",
                                                             created_by=User.objects.get(username="test1"),
                                                             contest=Contest.objects.get(title="titlex"),
                                                             sort_index="a")

    def test_visit_contest_problem_list_page_successfully(self):
        response = self.client.get('/contest/1/problems/')
        self.assertEqual(response.status_code, 200)

    def test_visit_contest_problem_page_unsuccessfully(self):
        response = self.client.get('/contest/1/problem/100/')
        self.assertTemplateUsed(response, "utils/error.html")


class ContestListPageTest(TestCase):
    # 以下是所有比赛列表页的测试
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user1.set_password("testaa")
        self.user1.save()
        self.url = reverse('contest_list_page')
        self.client.login(username="test1", password="testaa")
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PROTECTED_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))

    def test_visit_contest_list_page_successfully(self):
        response = self.client.get('/contests/')
        self.assertEqual(response.status_code, 200)

    def test_visit_contest_list_page_unsuccessfully(self):
        response = self.client.get('/contests/2/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_query_by_keyword(self):
        response = self.client.get(self.url + "?keyword=title1")
        self.assertEqual(response.status_code, 200)

    def test_query_by_join_successfully(self):
        response = self.client.get(self.url + "?join=True")
        self.assertEqual(response.status_code, 200)




