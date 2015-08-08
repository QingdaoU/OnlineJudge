# coding=utf-8
from django.core.paginator import Paginator

from rest_framework.response import Response


def error_response(error_reason):
    return Response(data={"code": 1, "data": error_reason})


def serializer_invalid_response(serializer):
    return error_response(serializer.errors)


def success_response(data):
    return Response(data={"code": 0, "data": data})


def paginate(request, query_set, object_serializer):
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
    参数错误的时候，返回{"code": 1, "data": u"参数错误"}
    返回的数据格式
    {
        "code": 0,
        "data": {
            "previous_page": null,
            "results": [
                {
                    "username": "1111111",
                    "password": "123456"
                }
            ],
            "next_page": 2
        }
    }
    :param query_set 数据库查询结果
    :param object_serializer: 序列化单个object的serializer
    :return response
    """
    need_paginate = request.GET.get("paging", None)
    # 如果请求的参数里面没有paging=true的话 就返回全部数据
    if need_paginate != "true":
        return success_response(data=object_serializer(query_set, many=True).data)

    page_size = request.GET.get("page_size", None)
    if not page_size:
        return error_response(u"参数错误")

    try:
        page_size = int(page_size)
    except Exception:
        return error_response(u"参数错误")

    paginator = Paginator(query_set, page_size)
    page = request.GET.get("page", None)

    try:
        current_page = paginator.page(page)
    except Exception:
        return error_response(u"参数错误")

    data = {"results": object_serializer(current_page, many=True).data,
            "previous_page": None,
            "next_page": None,
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

    return success_response(data)
