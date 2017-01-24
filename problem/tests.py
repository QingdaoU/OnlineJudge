from utils.api.tests import APITestCase

from .models import ProblemTag


class ProblemTagListAPITest(APITestCase):
    def test_get_tag_list(self):
        ProblemTag.objects.create(name="name1")
        ProblemTag.objects.create(name="name2")
        resp = self.client.get(self.reverse("problem_tag_list_api"))
        self.assertSuccess(resp)
        self.assertEqual(resp.data["data"], ["name1", "name2"])
