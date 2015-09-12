# coding=utf-8
import json
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from account.models import User, REGULAR_USER, ADMIN, SUPER_ADMIN
from problem.models import Problem
from contest.models import Contest
from contest.models import GROUP_CONTEST, PUBLIC_CONTEST, PASSWORD_PUBLIC_CONTEST
from submission.models import Submission
from rest_framework.test import APITestCase, APIClient


class SubmissionsListPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="gogoing", admin_type=REGULAR_USER)
        self.user2 = User.objects.create(username="cool", admin_type=REGULAR_USER)
        self.user2.set_password("666666")
        self.user.set_password("666666")
        self.user.save()
        self.user2.save()
        self.submission = Submission.objects.create(user_id=self.user.id,
                                                    language=1,
                                                    code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                    problem_id=1)

    def test_visit_submissionsListPage_successfully(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/submissions/1/')
        self.assertEqual(response.status_code, 200)

    def test_visit_submissionsListPage_successfully_language_filter(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/submissions/?language=1')
        self.assertEqual(response.status_code, 200)

    def test_visit_submissionsListPage_successfully_result_filter(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/submissions/?result=1')
        self.assertEqual(response.status_code, 200)

    def test_visit_submissionsListPage_without_page_successfully(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/submissions/')
        self.assertEqual(response.status_code, 200)

    def test_submissionsListPage_does_not_exist(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/submissions/5/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_submissionsListPage_page_not_exist(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/submissions/999/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_submissionsListPage_have_no_submission(self):
        self.client.login(username="cool", password="666666")
        response = self.client.get('/submissions/')
        self.assertEqual(response.status_code, 200)


class SubmissionAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('submission_api')
        self.user1 = User.objects.create(username="test1", admin_type=REGULAR_USER)
        self.user1.set_password("testaa")
        self.user1.save()
        self.user2 = User.objects.create(username="test2", admin_type=SUPER_ADMIN)
        self.user2.set_password("testbb")
        self.user2.save()
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
                                              created_by=User.objects.get(username="test2"))
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PUBLIC_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test2"))

        self.submission = Submission.objects.create(user_id=self.user1.id,
                                                    language=1,
                                                    code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                    problem_id=self.problem.id)

    def test_invalid_format(self):
        self.client.login(username="test1", password="testaa")
        data = {"language": 1}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_problem_does_not_exist(self):
        self.client.login(username="test1", password="testaa")
        data = {"language": 1, "code": '#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                "problem_id": self.problem.id + 10}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"题目不存在"})

    def test_submission_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"language": 1, "code": '#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                "problem_id": self.problem.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_submission_does_not_exist(self):
        self.client.login(username="test1", password="testaa")
        data = {"submission_id": self.submission.id + "111"}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"提交不存在"})

    def test_get_submission_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"submission_id": self.submission.id}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_parameter_error(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url)
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})


class SubmissionAdminAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('submission_admin_api_view')
        self.user = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user.set_password("testaa")
        self.user.save()
        self.client.login(username="test1", password="testaa")
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
                                              created_by=self.user)
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PUBLIC_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=self.user)

        self.submission = Submission.objects.create(user_id=self.user.id,
                                                    language=1,
                                                    code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                    problem_id=self.problem.id)

    def test_invalid_format(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})


class SubmissionPageTest(TestCase):
    # 单个题目的提交详情页
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user1.set_password("testaa")
        self.user1.save()
        self.user2 = User.objects.create(username="test2", admin_type=ADMIN)
        self.user2.set_password("testbb")
        self.user2.save()
        self.client.login(username="test1", password="testaa")
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
                                              created_by=User.objects.get(username="test1"))
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=PASSWORD_PUBLIC_CONTEST, show_rank=True,
                                                     show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=User.objects.get(username="test1"))

        self.submission = Submission.objects.create(user_id=self.user1.id,
                                                    language=1,
                                                    code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                    problem_id=self.problem.id)
