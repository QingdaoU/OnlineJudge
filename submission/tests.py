from django.test import TestCase
from account.models import User, REGULAR_USER
from submission.models import Submission
from rest_framework.test import APITestCase, APIClient


class SubmissionsListPageTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="gogoing", admin_type=REGULAR_USER)
        self.user2 = User.objects.create(username="cool", admin_type=REGULAR_USER)
        self.user2.set_password("666666")
        self.user.set_password("666666")
        self.user.save()
        # self.client.login(username="gogoing", password="666666")
        self.submission = Submission.objects.create(user_id=self.user.id,
                                                    language=1,
                                                    code='#include "stdio.h"\nint main(){\n\treturn 0;\n}',
                                                    problem_id=1)

    def test_visit_submissionsListPage_successfully(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/my_submissions/1/')
        self.assertEqual(response.status_code, 200)

    def test_visit_submissionsListPage_without_page_successfully(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/my_submissions/')
        self.assertEqual(response.status_code, 200)

    def test_submissionsListPage_does_not_exist(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/my_submissions/5/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_submissionsListPage_page_not_exist(self):
        self.client.login(username="gogoing", password="666666")
        response = self.client.get('/my_submissions/5/')
        self.assertTemplateUsed(response, "utils/error.html")

    def test_submissionsListPage_have_no_submission(self):
        self.client.login(username="cool", password="666666")
        response = self.client.get('/my_submissions/')
        self.assertEqual(response.status_code, 200)
