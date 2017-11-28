from utils.api.tests import APITestCase

from .models import Announcement


class AnnouncementAdminTest(APITestCase):
    def setUp(self):
        self.user = self.create_super_admin()
        self.url = self.reverse("announcement_admin_api")

    def test_announcement_list(self):
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def create_announcement(self):
        return self.client.post(self.url, data={"title": "test", "content": "test", "visible": True})

    def test_create_announcement(self):
        resp = self.create_announcement()
        self.assertSuccess(resp)
        return resp

    def test_edit_announcement(self):
        data = {"id": self.create_announcement().data["data"]["id"], "title": "ahaha", "content": "test content",
                "visible": False}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)
        resp_data = resp.data["data"]
        self.assertEqual(resp_data["title"], "ahaha")
        self.assertEqual(resp_data["content"], "test content")
        self.assertEqual(resp_data["visible"], False)

    def test_delete_announcement(self):
        id = self.test_create_announcement().data["data"]["id"]
        resp = self.client.delete(self.url + "?id=" + str(id))
        self.assertSuccess(resp)
        self.assertFalse(Announcement.objects.filter(id=id).exists())


class AnnouncementAPITest(APITestCase):
    def setUp(self):
        self.user = self.create_super_admin()
        Announcement.objects.create(title="title", content="content", visible=True, created_by=self.user)
        self.url = self.reverse("announcement_api")

    def test_get_announcement_list(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
