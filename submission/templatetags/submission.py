# coding=utf-8


def translate_result(value):
    print value
    results = {
        0: "Accepted",
        1: "Runtime Error",
        2: "Time Limit Exceeded",
        3: "Memory Limit Exceeded",
        4: "Compile Error",
        5: "Format Error",
        6: "Wrong Answer",
        7: "System Error",
        8: "Waiting"
    }
    return results[value]


def translate_id(submission_item):
    print submission_item
    return submission_item["_id"]

from django import template

register = template.Library()
register.filter("translate_result", translate_result)
register.filter("translate_id", translate_id)