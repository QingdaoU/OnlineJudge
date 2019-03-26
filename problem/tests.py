import copy
import hashlib
import os
import shutil
from datetime import timedelta
from zipfile import ZipFile

from django.conf import settings

from utils.api.tests import APITestCase

from .models import ProblemTag, ProblemIOMode
from .models import Problem, ProblemRuleType
from contest.models import Contest
from contest.tests import DEFAULT_CONTEST_DATA

from .views.admin import TestCaseAPI
from .utils import parse_problem_template

DEFAULT_PROBLEM_DATA = {"_id": "A-110", "title": "test", "description": "<p>test</p>", "input_description": "test",
                        "output_description": "test", "time_limit": 1000, "memory_limit": 256, "difficulty": "Low",
                        "visible": True, "tags": ["test"], "languages": ["C", "C++", "Java", "Python2"], "template": {},
                        "samples": [{"input": "test", "output": "test"}], "spj": False, "spj_language": "C",
                        "spj_code": "", "spj_compile_ok": True, "test_case_id": "499b26290cc7994e0b497212e842ea85",
                        "test_case_score": [{"output_name": "1.out", "input_name": "1.in", "output_size": 0,
                                             "stripped_output_md5": "d41d8cd98f00b204e9800998ecf8427e",
                                             "input_size": 0, "score": 0}],
                        "io_mode": {"io_mode": ProblemIOMode.standard, "input": "input.txt", "output": "output.txt"},
                        "share_submission": False,
                        "rule_type": "ACM", "hint": "<p>test</p>", "source": "test"}


class ProblemCreateTestBase(APITestCase):
    @staticmethod
    def add_problem(problem_data, created_by):
        data = copy.deepcopy(problem_data)
        if data["spj"]:
            if not data["spj_language"] or not data["spj_code"]:
                raise ValueError("Invalid spj")
            data["spj_version"] = hashlib.md5(
                (data["spj_language"] + ":" + data["spj_code"]).encode("utf-8")).hexdigest()
        else:
            data["spj_language"] = None
            data["spj_code"] = None
        if data["rule_type"] == ProblemRuleType.OI:
            total_score = 0
            for item in data["test_case_score"]:
                if item["score"] <= 0:
                    raise ValueError("invalid score")
                else:
                    total_score += item["score"]
            data["total_score"] = total_score
        data["created_by"] = created_by
        tags = data.pop("tags")

        data["languages"] = list(data["languages"])

        problem = Problem.objects.create(**data)

        for item in tags:
            try:
                tag = ProblemTag.objects.get(name=item)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=item)
            problem.tags.add(tag)
        return problem


class ProblemTagListAPITest(APITestCase):
    def test_get_tag_list(self):
        ProblemTag.objects.create(name="name1")
        ProblemTag.objects.create(name="name2")
        resp = self.client.get(self.reverse("problem_tag_list_api"))
        self.assertSuccess(resp)


class TestCaseUploadAPITest(APITestCase):
    def setUp(self):
        self.api = TestCaseAPI()
        self.url = self.reverse("test_case_api")
        self.create_super_admin()

    def test_filter_file_name(self):
        self.assertEqual(self.api.filter_name_list(["1.in", "1.out", "2.in", ".DS_Store"], spj=False),
                         ["1.in", "1.out"])
        self.assertEqual(self.api.filter_name_list(["2.in", "2.out"], spj=False), [])

        self.assertEqual(self.api.filter_name_list(["1.in", "1.out", "2.in"], spj=True), ["1.in", "2.in"])
        self.assertEqual(self.api.filter_name_list(["2.in", "3.in"], spj=True), [])

    def make_test_case_zip(self):
        base_dir = os.path.join("/tmp", "test_case")
        shutil.rmtree(base_dir, ignore_errors=True)
        os.mkdir(base_dir)
        file_names = ["1.in", "1.out", "2.in", ".DS_Store"]
        for item in file_names:
            with open(os.path.join(base_dir, item), "w", encoding="utf-8") as f:
                f.write(item + "\n" + item + "\r\n" + "end")
        zip_file = os.path.join(base_dir, "test_case.zip")
        with ZipFile(os.path.join(base_dir, "test_case.zip"), "w") as f:
            for item in file_names:
                f.write(os.path.join(base_dir, item), item)
        return zip_file

    def test_upload_spj_test_case_zip(self):
        with open(self.make_test_case_zip(), "rb") as f:
            resp = self.client.post(self.url,
                                    data={"spj": "true", "file": f}, format="multipart")
            self.assertSuccess(resp)
            data = resp.data["data"]
            self.assertEqual(data["spj"], True)
            test_case_dir = os.path.join(settings.TEST_CASE_DIR, data["id"])
            self.assertTrue(os.path.exists(test_case_dir))
            for item in data["info"]:
                name = item["input_name"]
                with open(os.path.join(test_case_dir, name), "r", encoding="utf-8") as f:
                    self.assertEqual(f.read(), name + "\n" + name + "\n" + "end")

    def test_upload_test_case_zip(self):
        with open(self.make_test_case_zip(), "rb") as f:
            resp = self.client.post(self.url,
                                    data={"spj": "false", "file": f}, format="multipart")
            self.assertSuccess(resp)
            data = resp.data["data"]
            self.assertEqual(data["spj"], False)
            test_case_dir = os.path.join(settings.TEST_CASE_DIR, data["id"])
            self.assertTrue(os.path.exists(test_case_dir))
            for item in data["info"]:
                name = item["input_name"]
                with open(os.path.join(test_case_dir, name), "r", encoding="utf-8") as f:
                    self.assertEqual(f.read(), name + "\n" + name + "\n" + "end")


class ProblemAdminAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("problem_admin_api")
        self.create_super_admin()
        self.data = copy.deepcopy(DEFAULT_PROBLEM_DATA)

    def test_create_problem(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        return resp

    def test_duplicate_display_id(self):
        self.test_create_problem()

        resp = self.client.post(self.url, data=self.data)
        self.assertFailed(resp, "Display ID already exists")

    def test_spj(self):
        data = copy.deepcopy(self.data)
        data["spj"] = True

        resp = self.client.post(self.url, data)
        self.assertFailed(resp, "Invalid spj")

        data["spj_code"] = "test"
        resp = self.client.post(self.url, data=data)
        self.assertSuccess(resp)

    def test_get_problem(self):
        self.test_create_problem()
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_get_one_problem(self):
        problem_id = self.test_create_problem().data["data"]["id"]
        resp = self.client.get(self.url + "?id=" + str(problem_id))
        self.assertSuccess(resp)

    def test_edit_problem(self):
        problem_id = self.test_create_problem().data["data"]["id"]
        data = copy.deepcopy(self.data)
        data["id"] = problem_id
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)


class ProblemAPITest(ProblemCreateTestBase):
    def setUp(self):
        self.url = self.reverse("problem_api")
        admin = self.create_admin(login=False)
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, admin)
        self.create_user("test", "test123")

    def test_get_problem_list(self):
        resp = self.client.get(f"{self.url}?limit=10")
        self.assertSuccess(resp)

    def get_one_problem(self):
        resp = self.client.get(self.url + "?id=" + self.problem._id)
        self.assertSuccess(resp)


class ContestProblemAdminTest(APITestCase):
    def setUp(self):
        self.url = self.reverse("contest_problem_admin_api")
        self.create_admin()
        self.contest = self.client.post(self.reverse("contest_admin_api"), data=DEFAULT_CONTEST_DATA).data["data"]

    def test_create_contest_problem(self):
        data = copy.deepcopy(DEFAULT_PROBLEM_DATA)
        data["contest_id"] = self.contest["id"]
        resp = self.client.post(self.url, data=data)
        self.assertSuccess(resp)
        return resp.data["data"]

    def test_get_contest_problem(self):
        self.test_create_contest_problem()
        contest_id = self.contest["id"]
        resp = self.client.get(self.url + "?contest_id=" + str(contest_id))
        self.assertSuccess(resp)
        self.assertEqual(len(resp.data["data"]["results"]), 1)

    def test_get_one_contest_problem(self):
        contest_problem = self.test_create_contest_problem()
        contest_id = self.contest["id"]
        problem_id = contest_problem["id"]
        resp = self.client.get(f"{self.url}?contest_id={contest_id}&id={problem_id}")
        self.assertSuccess(resp)


class ContestProblemTest(ProblemCreateTestBase):
    def setUp(self):
        admin = self.create_admin()
        url = self.reverse("contest_admin_api")
        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["password"] = ""
        contest_data["start_time"] = contest_data["start_time"] + timedelta(hours=1)
        self.contest = self.client.post(url, data=contest_data).data["data"]
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, admin)
        self.problem.contest_id = self.contest["id"]
        self.problem.save()
        self.url = self.reverse("contest_problem_api")

    def test_admin_get_contest_problem_list(self):
        contest_id = self.contest["id"]
        resp = self.client.get(self.url + "?contest_id=" + str(contest_id))
        self.assertSuccess(resp)
        self.assertEqual(len(resp.data["data"]), 1)

    def test_admin_get_one_contest_problem(self):
        contest_id = self.contest["id"]
        problem_id = self.problem._id
        resp = self.client.get("{}?contest_id={}&problem_id={}".format(self.url, contest_id, problem_id))
        self.assertSuccess(resp)

    def test_regular_user_get_not_started_contest_problem(self):
        self.create_user("test", "test123")
        resp = self.client.get(self.url + "?contest_id=" + str(self.contest["id"]))
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest has not started yet."})

    def test_reguar_user_get_started_contest_problem(self):
        self.create_user("test", "test123")
        contest = Contest.objects.first()
        contest.start_time = contest.start_time - timedelta(hours=1)
        contest.save()
        resp = self.client.get(self.url + "?contest_id=" + str(self.contest["id"]))
        self.assertSuccess(resp)


class AddProblemFromPublicProblemAPITest(ProblemCreateTestBase):
    def setUp(self):
        admin = self.create_admin()
        url = self.reverse("contest_admin_api")
        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["password"] = ""
        contest_data["start_time"] = contest_data["start_time"] + timedelta(hours=1)
        self.contest = self.client.post(url, data=contest_data).data["data"]
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, admin)
        self.url = self.reverse("add_contest_problem_from_public_api")
        self.data = {
            "display_id": "1000",
            "contest_id": self.contest["id"],
            "problem_id": self.problem.id
        }

    def test_add_contest_problem(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        self.assertTrue(Problem.objects.all().exists())
        self.assertTrue(Problem.objects.filter(contest_id=self.contest["id"]).exists())


class ParseProblemTemplateTest(APITestCase):
    def test_parse(self):
        template_str = """
//PREPEND BEGIN
aaa
//PREPEND END

//TEMPLATE BEGIN
bbb
//TEMPLATE END

//APPEND BEGIN
ccc
//APPEND END
"""

        ret = parse_problem_template(template_str)
        self.assertEqual(ret["prepend"], "aaa\n")
        self.assertEqual(ret["template"], "bbb\n")
        self.assertEqual(ret["append"], "ccc\n")

    def test_parse1(self):
        template_str = """
//PREPEND BEGIN
aaa
//PREPEND END

//APPEND BEGIN
ccc
//APPEND END
//APPEND BEGIN
ddd
//APPEND END
"""

        ret = parse_problem_template(template_str)
        self.assertEqual(ret["prepend"], "aaa\n")
        self.assertEqual(ret["template"], "")
        self.assertEqual(ret["append"], "ccc\n")
