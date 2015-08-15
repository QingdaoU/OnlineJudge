# coding=utf-8


def get_problem_accepted_radio(problem):
    if problem.total_accepted_number:
        return int((problem.total_accepted_number * 100) / problem.total_submit_number)
    return 0


from django import template


register = template.Library()
register.filter("accepted_radio", get_problem_accepted_radio)
