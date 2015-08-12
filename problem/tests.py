# coding=utf-8
import json

from django.test import TestCase

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APIClient

from account.models import User, SUPER_ADMIN
from problem.models import Problem, ProblemTag


class ProblemPageTest(TestCase):
    pass


class ProblemAdminTest(APITestCase):
    def _create_data(self, problem_id, visible, tags):
        data = {"id": problem_id,
                "title": "title1",
                "description": "des1",
                "test_case_id": "1",
                "source": "source1",
                "samples": [{"input": "1 1", "output": "2"}],
                "time_limit": "100",
                "memory_limit": "1000",
                "difficulty": "1",
                "hint": "hint1",
                "visible": visible,
                "tags": tags}
        return data

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("problem_admin_api")
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.client.login(username="test", password="testaa")
        ProblemTag.objects.create(name="tag1")
        ProblemTag.objects.create(name="tag2")
        self.problem = Problem.objects.create(title="title1",
                                              description="des1",
                                              test_case_id="1",
                                              source="source1",
                                              samples=[{"input": "1 1", "output": "2"}],
                                              time_limit=100,
                                              memory_limit=1000,
                                              difficulty=1,
                                              hint="hint1",
                                              created_by=User.objects.get(username="test"))

    # 以下是发布题目的测试
    def test_invalid_format(self):
        data = {"title": "test1"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_release_problem_successfully(self):
        data = {"title": "title1",
                "description": "des1",
                "test_case_id": "1",
                "source": "source1",
                "samples": [{"input": "1 1", "output": "2"}],
                "time_limit": "100",
                "memory_limit": "1000",
                "difficulty": "1",
                "hint": "hint1",
                "tags": [1]}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.data["code"], 0)

    # 以下是编辑题目的测试
    def test_invalid_data(self):
        data = {"title": "test0"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_problem_does_not_exist(self):
        tags = ProblemTag.objects.filter(id__in=[1])
        self.problem.tags.add(*tags)
        data = self._create_data(2, False, [1])
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.data, {"code": 1, "data": u"该题目不存在！"})

    def test_edit_problem_successfully(self):
        tags = ProblemTag.objects.filter(id__in=[1])
        self.problem.tags.add(*tags)
        data = self._create_data(1, True, [1, 2])
        problem = Problem.objects.get(id=data["id"])
        problem.tags.remove(*problem.tags.all())
        problem.tags.add(*ProblemTag.objects.filter(id__in=data["tags"]))
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.data["code"], 0)
