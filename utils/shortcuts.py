# coding=utf-8
import json
import logging
import random

from django.http import HttpResponse
from django.views.generic import View

logger = logging.getLogger(__name__)


def JSONResponse(data, content_type="application/json"):
    resp = HttpResponse(json.dumps(data, indent=4), content_type=content_type)
    resp.data = data
    return resp


class APIView(View):
    def _get_request_json(self, request):
        if request.method != "GET":
            body = request.body
            if body:
                return json.loads(body.decode("utf-8"))
            return {}
        return request.GET

    def success(self, data=None):
        return JSONResponse({"error": None, "data": data})

    def error(self, message, error="error"):
        return JSONResponse({"error": error, "data": message})

    def invalid_serializer(self, serializer):
        for k, v in serializer.errors.items():
            return self.error(k + ": " + v[0], error="invalid-data-format")

    def server_error(self):
        return self.error("Server Error")

    def dispatch(self, request, *args, **kwargs):
        try:
            request.data = self._get_request_json(self.request)
        except ValueError:
            return self.error("Invalid JSON")
        try:
            return super(APIView, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            logging.exception(e)
            return self.server_error()


def paginate_data(request, query_set, object_serializer):
    """
    用于分页的函数
    如果 url 里面不含有paging=true，那么将返回全部数据。类似
    [
        {
            "username": "1111111",
            "password": "123456"
        }
    ]
    如果 url 中有 paging=true 的参数，
    然后还需要读取其余的两个参数，page=[int]，需要的页码
    page_size=[int]，一页的数据条数
    :param request
    :param query_set 数据库查询结果
    :param object_serializer: 序列化单个object的serializer
    """
    need_paginate = request.GET.get("paging", None)
    # 如果请求的参数里面没有paging=true的话 就返回全部数据
    if need_paginate != "true":
        if object_serializer:
            return object_serializer(query_set, many=True).data
        else:
            return query_set

    try:
        limit = int(request.GET.get("limit", "100"))
    except ValueError:
        limit = 100
    if limit < 0:
        limit = 100

    try:
        offset = int(request.GET.get("offset", "0"))
    except ValueError:
        offset = 0
    if offset < 0:
        offset = 0

    results = query_set[offset:offset + limit]
    if object_serializer:
        count = query_set.count()
        results = object_serializer(results, many=True).data
    else:
        count = len(query_set)

    data = {"results": results,
            "count": count}

    return data


def rand_str(length=32, type="lower_hex"):
    """
    生成指定长度的随机字符串或者数字, 只用于随机编号等, 不要用于密钥等场景
    :param length: 字符串或者数字的长度
    :param type: str 代表随机字符串，num 代表随机数字
    :return: 字符串
    """
    if type == "str":
        return ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for i in range(length))
    elif type == "lower_str":
        return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(length))
    elif type == "lower_hex":
        return ''.join(random.choice("0123456789abcdef") for i in range(length))
    else:
        return random.choice("123456789") + ''.join(random.choice("0123456789") for i in range(length - 1))