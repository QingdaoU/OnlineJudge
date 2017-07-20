import copy
from datetime import datetime, timedelta

from django.utils import timezone

from utils.api._serializers import DateTimeTZField
from utils.api.tests import APITestCase

from .models import ContestAnnouncement, ContestRuleType

DEFAULT_CONTEST_DATA = {"title": "test title", "description": "test description",
                        "start_time": timezone.localtime(timezone.now()),
                        "end_time": timezone.localtime(timezone.now()) + timedelta(days=1),
                        "rule_type": ContestRuleType.ACM,
                        "password": "123",
                        "visible": True, "real_time_rank": True}


class ContestAdminAPITest(APITestCase):
    def setUp(self):
        self.create_super_admin()
        self.url = self.reverse("contest_admin_api")
        self.data = DEFAULT_CONTEST_DATA

    def test_create_contest(self):
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_update_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        update_data = {"id": id, "title": "update title",
                       "description": "update description",
                       "password": "12345",
                       "visible": False, "real_time_rank": False}
        data = copy.deepcopy(self.data)
        data.update(update_data)
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        response_data = response.data["data"]
        datetime_tz_field = DateTimeTZField()
        for k in data.keys():
            if isinstance(data[k], datetime):
                data[k] = datetime_tz_field.to_representation(data[k])
            self.assertEqual(response_data[k], data[k])

    def test_get_contests(self):
        self.test_create_contest()
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_get_one_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)


class ContestAPITest(APITestCase):
    def setUp(self):
        self.create_admin()
        self.url = self.reverse("contest_api")

    def create_contest(self):
        url = self.reverse("contest_admin_api")
        return self.client.post(url, data=DEFAULT_CONTEST_DATA)

    def test_get_contest_list(self):
        self.create_contest()
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_get_one_contest(self):
        contest_id = self.create_contest().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, contest_id))
        self.assertSuccess(response)

    def test_contest_password(self):
        contest_id = self.create_contest().data["data"]["id"]
        self.create_user("test", "test123")
        url = self.reverse("contest_password_api")
        resp = self.client.post(url, {"contest_id": contest_id, "password": "error_password"})
        self.assertFailed(resp)

        resp = self.client.post(url, {"contest_id": contest_id, "password": DEFAULT_CONTEST_DATA["password"]})
        self.assertSuccess(resp)

    def test_contest_access(self):
        contest_id = self.create_contest().data["data"]["id"]
        self.create_user("test", "test123")
        url = self.reverse("contest_access_api")
        resp = self.client.get(url + "?contest_id=" + str(contest_id))
        self.assertFalse(resp.data["data"]["Access"])

        password_url = self.reverse("contest_password_api")
        resp = self.client.post(password_url, {"contest_id": contest_id, "password": DEFAULT_CONTEST_DATA["password"]})
        self.assertSuccess(resp)
        resp = self.client.get(url + "?contest_id=" + str(contest_id))
        self.assertSuccess(resp)

    # def test_get_not_started_contest(self):
    #     contest_id = self.create_contest().data["data"]["id"]
    #     resp = self.client.get(self.url + "?id=" + str(contest_id))
    #     self.assertSuccess(resp)
    #
    #     self.create_user("test", "1234")
    #     url = self.reverse("contest_password_api")
    #     resp = self.client.post(url, {"contest_id": contest_id, "password": DEFAULT_CONTEST_DATA["password"]})
    #     self.assertSuccess(resp)
    #     resp = self.client.get(self.url + "?id=" + str(contest_id))
    #     self.assertFailed(resp)


class ContestAnnouncementAPITest(APITestCase):
    def setUp(self):
        self.create_super_admin()
        self.url = self.reverse("contest_announcement_admin_api")
        contest_id = self.create_contest().data["data"]["id"]
        self.data = {"title": "test title", "content": "test content", "contest_id": contest_id}

    def create_contest(self):
        url = self.reverse("contest_admin_api")
        data = DEFAULT_CONTEST_DATA
        return self.client.post(url, data=data)

    def test_create_contest_announcement(self):
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_delete_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        response = self.client.delete("{}?id={}".format(self.url, id))
        self.assertSuccess(response)
        self.assertFalse(ContestAnnouncement.objects.filter(id=id).exists())

    def test_get_contest_announcements(self):
        self.test_create_contest_announcement()
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_get_one_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)


class ContestAnnouncementListAPITest(APITestCase):
    def setUp(self):
        self.create_super_admin()
        self.url = self.reverse("contest_announcement_api")

    def create_contest_announcements(self):
        contest_id = self.client.post(self.reverse("contest_admin_api"), data=DEFAULT_CONTEST_DATA).data["data"]["id"]
        url = self.reverse("contest_announcement_admin_api")
        self.client.post(url, data={"title": "test title1", "content": "test content1", "contest_id": contest_id})
        self.client.post(url, data={"title": "test title2", "content": "test content2", "contest_id": contest_id})
        return contest_id

    def test_get_contest_announcement_list(self):
        contest_id = self.create_contest_announcements()
        response = self.client.get(self.url, data={"contest_id": contest_id})
        self.assertSuccess(response)
