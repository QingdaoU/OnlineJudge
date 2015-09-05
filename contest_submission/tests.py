import json

from django.core.urlresolvers import reverse
from account.models import User, ADMIN, SUPER_ADMIN

from contest.models import Contest, ContestProblem
from submission.models import Submission
from rest_framework.test import APITestCase, APIClient


# Create your tests here.

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
