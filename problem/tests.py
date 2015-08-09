# coding=utf-8
from django.test import TestCase

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APIClient

from account.models import User, SUPER_ADMIN
from problem.models import Problem, ProblemTag


class ProblemPageTest(TestCase):
    pass


class ProblemAdminTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("problem_admin_api")
        user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        user.set_password("testaa")
        user.save()

    # 以下是发布题目的测试
    def test_invalid_format(self):
        self.client.login(username="test", password="testaa")
        data = {"title": "test1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_success_problem(self):
        self.client.login(username="test", password="testaa")
        ProblemTag.objects.create(name="tag1", description="destag1")
        data = {"title": "title1", "description": "des1", "test_case_id": "1", "source": "source1",
                "sample": [{"input": "1 1", "output": "2"}], "time_limit": "100", "memory_limit": "1000",
                "difficulty": "1", "hint": "hint1", "tags": [1]}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    # 以下是编辑题目的测试
    def test_put_invalid_data(self):
        self.client.login(username="test", password="testaa")
        data = {"title": "test0"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_problem_does_not_exist(self):
        self.client.login(username="test", password="testaa")
        ProblemTag.objects.create(name="tag1", description="destag1")
        tags = ProblemTag.objects.filter(id__in=[1])
        problem = Problem.objects.create(title="title1", description="des1",
                                         test_case_id="1", source="source1",
                                         sample=[{"input": "1 1", "output": "2"}],
                                         time_limit=100, memory_limit=1000,
                                         difficulty=1, hint="hint1",
                                         created_by=User.objects.get(username="test"))
        problem.tags.add(*tags)
        data = {"id": 2, "title": "title1", "description": "des1", "test_case_id": "1", "source": "source1",
                "sample": [{"input": "1 1", "output": "2"}], "time_limit": "100", "memory_limit": "1000",
                "difficulty": "1", "hint": "hint1", "tags": [1]}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"该题目不存在！"})

    def test_success_edit_problem(self):
        self.client.login(username="test", password="testaa")
        self.client.login(username="test", password="testaa")
        ProblemTag.objects.create(name="tag1", description="destag1")
        ProblemTag.objects.create(name="tag2", description="destag2")
        tags = ProblemTag.objects.filter(id__in=[1])
        problem0 = Problem.objects.create(title="title1", description="des1",
                                          test_case_id="1", source="source1",
                                          sample=[{"input": "1 1", "output": "2"}],
                                          time_limit=100, memory_limit=1000,
                                          difficulty=1, hint="hint1",
                                          created_by=User.objects.get(username="test"))
        problem0.tags.add(*tags)
        data = {"id": 1, "title": "title1", "description": "des1", "test_case_id": "1", "source": "source1",
                "sample": [{"input": "1 1", "output": "2"}], "time_limit": "100", "memory_limit": "1000",
                "difficulty": "1", "hint": "hint1", "visible": True, "tags": [1, 2]}
        problem = Problem.objects.get(id=data["id"])
        problem.tags.remove(*problem.tags.all())
        problem.tags.add(*ProblemTag.objects.filter(id__in=data["tags"]))
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 0)
