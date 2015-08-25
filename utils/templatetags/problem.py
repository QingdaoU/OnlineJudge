# coding=utf-8


def get_problem_accepted_radio(problem):
    if problem.total_submit_number:
        return str(int((problem.total_accepted_number * 100) / problem.total_submit_number)) \
               + "% (" + str(problem.total_accepted_number) + "/" + str(problem.total_submit_number) + ")"
    return "0%"


from django import template

register = template.Library()
register.filter("accepted_radio", get_problem_accepted_radio)
