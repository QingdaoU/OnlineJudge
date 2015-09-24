# coding=utf-8


def get_problem_accepted_radio(problem):
    if problem.total_submit_number:
        return str(int((problem.total_accepted_number * 100) / problem.total_submit_number)) \
               + "% (" + str(problem.total_accepted_number) + " / " + str(problem.total_submit_number) + ")"
    return "0%"


def get_problem_status(problems_status, problem_id):
    # 用户没登陆 或者 user.problem_status 中没有这个字段都会到导致这里的problem_status 为 ""
    if not problems_status:
        return ""

    if str(problem_id) in problems_status:
        if problems_status[str(problem_id)] == 1:
            return "glyphicon glyphicon-ok ac-flag"
        return "glyphicon glyphicon-minus dealing-flag"
    return ""


from django import template

register = template.Library()
register.filter("accepted_radio", get_problem_accepted_radio)
register.simple_tag(get_problem_status, name="get_problem_status")
