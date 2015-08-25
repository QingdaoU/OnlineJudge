# coding=utf-8
from django import template


def translate_result(value):
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


def translate_language(value):
    return {1: "C", 2: "C++", 3: "Java"}[value]


def translate_result_class(value):
    if value == 0:
        return "success"
    elif value == 8:
        return "info"
    return "danger"


def get_contest_submission_problem_detail(contest_problem, my_submission):
    if contest_problem.id in my_submission:
        submission = my_submission[contest_problem.id]
        if submission.ac:
            return u"\n 时间: " + str(submission.total_time) + u" min"
    return ""


def get_submission_problem_result_class(contest_problem, my_submission):
    if contest_problem.id in my_submission:
        submission = my_submission[contest_problem.id]
        if submission.ac:
            return "success"
        else:
            return "danger"
    else:
        return ""

register = template.Library()
register.filter("translate_result", translate_result)
register.filter("translate_language", translate_language)
register.filter("translate_result_class", translate_result_class)
register.simple_tag(get_contest_submission_problem_detail, name="submission_problem")
register.simple_tag(get_submission_problem_result_class, name="submission_problem_result_class")