# coding=utf-8
import json

from django.test import TestCase, Client

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APIClient

from account.models import User, SUPER_ADMIN
from problem.models import Problem, ProblemTag


class ProblemPageTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.client.login(username="test", password="testaa")
        self.problem = Problem.objects.create(title="title1",
                                              description="description1",
                                              input_description="input1_description",
                                              output_description="output1_description",
                                              test_case_id="1",
                                              source="source1",
                                              samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                              time_limit=100,
                                              memory_limit=1000,
                                              difficulty=1,
                                              hint="hint1",
                                              created_by=User.objects.get(username="test"))

    def test_visit_problem_successfully(self):
        response = self.client.get('/problem/1/')
        self.assertEqual(response.status_code, 200)

    def test_problem_does_not_exist(self):
        response = self.client.get('/problem/3/')
        self.assertTemplateUsed(response, "utils/error.html")


class ProblemAdminTest(APITestCase):
    def _create_data(self, problem_id, visible, tags):
        data = {"id": problem_id,
                "title": "title0",
                "description": "description0",
                "input_description": "input_description0",
                "output_description": "output_description0",
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
                                              description="description1",
                                              input_description="input1_description",
                                              output_description="output1_description",
                                              test_case_id="1",
                                              source="source1",
                                              samples=json.dumps([{"input": "1 1", "output": "2"}]),
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
        data = {"title": "title2",
                "description": "description2",
                "input_description": "input_description2",
                "output_description": "output_description2",
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

    # 以下是题目分页的测试
    def test_success_get_data(self):
        self.assertEqual(self.client.get(self.url).data["code"], 0)

    def test_query_by_keyword(self):
        response = self.client.get(self.url + "?keyword=title1")
        self.assertEqual(response.data["code"], 0)

    def test_query_by_visible(self):
        response = self.client.get(self.url + "?visible=true")
        self.assertEqual(response.data["code"], 0)
        for item in response.data["data"]:
            self.assertEqual(item["visible"], True)

    def test_query_problem_does_not_exist(self):
        data = {"problem_id": 2}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"题目不存在"})

    def test_query_problem_exists(self):
        data = {"problem_id": self.problem.id}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data["code"], 0)


class ProblemTagAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('problem_tag_admin_api')
        self.user = User.objects.create(username="testx", admin_type=SUPER_ADMIN)
        self.user.set_password("testxx")
        self.user.save()
        self.client.login(username="testx", password="testxx")
        ProblemTag.objects.create(name="tag1")

    # 以下是返回所有的问题的标签
    def test_get_all_problem_tag_successfully(self):
        self.assertEqual(self.client.get(self.url).data["code"], 0)


class ProblemListPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('problem_list_page', kwargs={"page": 1})
        self.user = User.objects.create(username="test", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.client.login(username="test", password="testaa")
        ProblemTag.objects.create(name="tag1")
        ProblemTag.objects.create(name="tag2")
        self.problem = Problem.objects.create(title="title1",
                                              description="description1",
                                              input_description="input1_description",
                                              output_description="output1_description",
                                              test_case_id="1",
                                              source="source1",
                                              samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                              time_limit=100,
                                              memory_limit=1000,
                                              difficulty=1,
                                              hint="hint1",
                                              created_by=User.objects.get(username="test"))

    def test_problemListPage_not_exist(self):
        response = self.client.get('/problems/999/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_query_by_keyword(self):
        response = self.client.get(self.url + "?keyword=title1")
        self.assertEqual(response.status_code, 200)

    def test_query_by_tag_successfully(self):
        response = self.client.get(self.url + "?tag=")
        self.assertEqual(response.status_code, 200)

    def test_tag_does_not_exists(self):
        response = self.client.get(self.url + "?tag=xxxxxx")
        self.assertTemplateUsed(response, "utils/error.html")

