# coding=utf-8
import json
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from account.models import User, REGULAR_USER, ADMIN, SUPER_ADMIN
from problem.models import Problem
from contest.models import Contest, ContestProblem
from submission.models import Submission
from rest_framework.test import APITestCase, APIClient


class ContestSubmissionAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contest_submission_api')
        self.user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user1.set_password("testaa")
        self.user1.save()
        self.user2 = User.objects.create(username="test2", admin_type=REGULAR_USER)
        self.user2.set_password("testbb")
        self.user2.save()
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=1, show_rank=True, show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-30T12:00:00.000Z",
                                                     created_by=User.objects.get(username="test1"))
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

    # 以下是创建比赛的提交
    def test_invalid_format(self):
        self.client.login(username="test1", password="testaa")
        data = {"contest_id": self.global_contest.id, "language": 1}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 1)

    def test_contest_submission_successfully(self):
        self.client.login(username="test1", password="testaa")
        data = {"contest_id": self.global_contest.id, "problem_id": self.contest_problem.id,
                "language": 1, "code": '#include "stdio.h"\nint main(){\n\treturn 0;\n}'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data["code"], 0)

    def test_contest_problem_does_not_exist(self):
        self.client.login(username="test1", password="testaa")
        data = {"contest_id": self.global_contest.id, "problem_id": self.contest_problem.id + 10,
                "language": 1, "code": '#include "stdio.h"\nint main(){\n\treturn 0;\n}'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.data, {"code": 1, "data": u"题目不存在"})


class ContestProblemMySubmissionListTest(TestCase):
    # 以下是我比赛单个题目的提交列表的测试
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="test1", admin_type=SUPER_ADMIN)
        self.user1.set_password("testaa")
        self.user1.save()
        self.user2 = User.objects.create(username="test2", admin_type=REGULAR_USER)
        self.user2.set_password("testbb")
        self.user2.save()
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=1, show_rank=True, show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-30T12:00:00.000Z",
                                                     created_by=User.objects.get(username="test1"))
        self.contest_problem = ContestProblem.objects.create(title="titlex",
                                                             description="descriptionx",
                                                             input_description="input1_description",
                                                             output_description="output1_description",
                                                             test_case_id="1",
                                                             samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                                             time_limit=100,
                                                             memory_limit=1000,
                                                             hint="hint1",
                                                             created_by=self.user1,
                                                             contest=self.global_contest,
                                                             sort_index="a")

    def test_contestsList_page_not_exist(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get('/contest/1/submissions/999/')
        self.assertTemplateUsed(response, "utils/error.html")


class SubmissionAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contest_submission_admin_api_view')
        self.userA = User.objects.create(username="test1", admin_type=ADMIN)
        self.userA.set_password("testaa")
        self.userA.save()
        self.userS = User.objects.create(username="test2", admin_type=SUPER_ADMIN)
        self.userS.set_password("testbb")
        self.userS.save()
        self.global_contest = Contest.objects.create(title="titlex", description="descriptionx", mode=1,
                                                     contest_type=2, show_rank=True, show_user_submission=True,
                                                     start_time="2015-08-15T10:00:00.000Z",
                                                     end_time="2015-08-15T12:00:00.000Z",
                                                     password="aacc", created_by=self.userS
                                                     )
        self.problem = ContestProblem.objects.create(title="title1",
                                                     description="description1",
                                                     input_description="input1_description",
                                                     output_description="output1_description",
                                                     test_case_id="1",
                                                     sort_index="1",
                                                     samples=json.dumps([{"input": "1 1", "output": "2"}]),
                                                     time_limit=100,
                                                     memory_limit=1000,
                                                     hint="hint1",
                                                     contest=self.global_contest,
                                                     created_by=self.userS)
        self.submission = Submission.objects.create(user_id=self.userA.id,
                                                    language=1,
                                                    code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                    problem_id=self.problem.id)
        self.submissionS = Submission.objects.create(user_id=self.userS.id,
                                                     language=2,
                                                     code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                     problem_id=self.problem.id)

    def test_submission_contest_does_not_exist(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url + "?contest_id=99")
        self.assertEqual(response.data["code"], 1)

    def test_submission_contest_parameter_error(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url)
        self.assertEqual(response.data["code"], 1)

    def test_submission_access_denied(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?problem_id=" + str(self.problem.id))
        self.assertEqual(response.data["code"], 1)

    def test_submission_access_denied_with_contest_id(self):
        self.client.login(username="test1", password="testaa")
        response = self.client.get(self.url + "?contest_id=" + str(self.global_contest.id))
        self.assertEqual(response.data["code"], 1)

    def test_get_submission_successfully(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(
            self.url + "?contest_id=" + str(self.global_contest.id) + "&problem_id=" + str(self.problem.id))
        self.assertEqual(response.data["code"], 0)

    def test_get_submission_successfully_problem(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url + "?problem_id=" + str(self.problem.id))
        self.assertEqual(response.data["code"], 0)

    def test_get_submission_problem_do_not_exist(self):
        self.client.login(username="test2", password="testbb")
        response = self.client.get(self.url + "?problem_id=9999")
        self.assertEqual(response.data["code"], 1)
