# coding=utf-8
import os
import hashlib
import time
import random
import logging

from django.shortcuts import render
from django.core.paginator import Paginator

from rest_framework.response import Response


logger = logging.getLogger("app_info")


def error_page(request, error_reason):
    return render(request, "utils/error.html", {"error": error_reason})


def error_response(error_reason):
    return Response(data={"code": 1, "data": error_reason})


def serializer_invalid_response(serializer):
    for k, v in serializer.errors.iteritems():
        return error_response(k + " : " + v[0])


def success_response(data):
    return Response(data={"code": 0, "data": data})


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
    然后还需要读取其余的两个参数，page=[int]，需要的页码，p
    age_size=[int]，一页的数据条数

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

    page_size = request.GET.get("page_size", None)
    if not page_size:
        raise ValueError("Error parameter page_size")

    try:
        page_size = int(page_size)
    except Exception:
        raise ValueError("Error parameter page_size")

    paginator = Paginator(query_set, page_size)
    page = request.GET.get("page", None)

    try:
        current_page = paginator.page(page)
    except Exception:
        raise ValueError("Error parameter current_page")
    if object_serializer:
        results = object_serializer(current_page, many=True).data
    else:
        results = current_page

    data = {"results": results,
            "previous_page": None,
            "next_page": None,
            "page_size": page_size,
            "current_page": page,
            "count": paginator.count,
            "total_page": paginator.num_pages}

    try:
        data["previous_page"] = current_page.previous_page_number()
    except Exception:
        pass

    try:
        data["next_page"] = current_page.next_page_number()
    except Exception:
        pass

    return data


def paginate(request, query_set, object_serializer=None):
    try:
        data= paginate_data(request, query_set, object_serializer)
    except Exception as e:
        logger.error(str(e))
        return error_response(u"参数错误")
    return success_response(data)


def rand_str(length=32):
    if length > 128:
        raise ValueError("length must <= 128")
    return hashlib.sha512(os.urandom(128)).hexdigest()[0:length]


def build_query_string(kv_data, ignore_none=True):
    # {"a": 1, "b": "test"} -> "?a=1&b=test"
    query_string = ""
    for k, v in kv_data.iteritems():
        if ignore_none is True and kv_data[k] is None:
            continue
        if query_string != "":
            query_string += "&"
        else:
            query_string = "?"
        query_string += (k + "=" + str(v))
    return query_string
