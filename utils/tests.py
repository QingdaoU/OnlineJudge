# coding=utf-8
from rest_framework.test import APIClient, APITestCase
from rest_framework import serializers
from rest_framework.decorators import api_view

from account.models import User
from .shortcuts import paginate


class PaginationTestSerialiser(serializers.Serializer):
    username = serializers.CharField(max_length=100)


@api_view(["GET"])
def pagination_test_func(request):
    return paginate(request, User.objects.all(), PaginationTestSerialiser)


class PaginatorTest(APITestCase):
    urls = "utils.test_urls"

    def setUp(self):
        self.client = APIClient()
        self.url = "/paginate_test/"
        User.objects.create(username="test1")
        User.objects.create(username="test2")

    def test_no_paginate(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["code"], 0)
        self.assertNotIn("next_page", response.data["data"])
        self.assertNotIn("previous_page", response.data["data"])

    def test_error_parameter(self):
        response = self.client.get(self.url + "?paging=true")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})

        response = self.client.get(self.url + "?paging=true&page_size=-1")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})

        response = self.client.get(self.url + "?paging=true&page_size=aa")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})

        response = self.client.get(self.url + "?paging=true&page_size=1&page=-1")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})

        response = self.client.get(self.url + "?paging=true&page_size=aaa&page=1")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})

        response = self.client.get(self.url + "?paging=true&page_size=1&page=aaa")
        self.assertEqual(response.data, {"code": 1, "data": u"参数错误"})

    def test_correct_paginate(self):
        response = self.client.get(self.url + "?paging=true&page_size=1&page=1")
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"]["previous_page"], None)
        self.assertEqual(response.data["data"]["next_page"], 2)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["count"], 2)
        self.assertEqual(response.data["data"]["total_page"], 2)

        response = self.client.get(self.url + "?paging=true&page_size=2&page=1")
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"]["previous_page"], None)
        self.assertEqual(response.data["data"]["next_page"], None)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        self.assertEqual(response.data["data"]["count"], 2)
        self.assertEqual(response.data["data"]["total_page"], 1)
