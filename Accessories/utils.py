import django
from contest.models import Contest
django.setup()

def add_exist_problem_to_contest(problems, contest_id):
    for problem in problems:
        print problem.title

    return
