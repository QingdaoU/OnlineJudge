# coding=utf-8
from rest_framework.response import Response


def error_response(error_reason):
    return Response(data={"code": 1, "data": error_reason})


def serializer_invalid_response(serializer):
    return error_response(serializer.errors)


def success_response(data):
    return Response(data={"code": 0, "data": data})