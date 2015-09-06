import django
from contest.models import *
from problem.models import *
django.setup()


def add_exist_problem_to_contest(problems, contest_id):
    try:
        contest = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        print "Contest Doesn't Exist!"
        return
    i = 1
    for problem in problems:
        print "Add the problem:"
        print problem.title
        print "The sort Index is" + str(i) + " You Can modify it latter as you like~"
        ContestProblem.objects.create(contest=contest, sort_index=str(i),
                              title=problem.title, description=problem.description,
                              input_description=problem.input_description,
                              output_description=problem.output_description,
                              samples=problem.samples,
                              test_case_id=problem.test_case_id,
                              hint=problem.hint,
                              created_by=problem.created_by,
                              time_limit=problem.time_limit,
                              memory_limit=problem.memory_limit)
        i += 1
    return

def add_contest_problem_to_problem(contest_id):
    try:
        contest = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        print "Contest Doesn't Exist!"
        return
    #Get all problems in this contest
    problems = ContestProblem.objects.filter(contest=contest)
    
    #get a tag
    try:
        tag = ProblemTag.objects.get(name=contest.title)
    except ProblemTag.DoesNotExist:
        tag = ProblemTag.objects.create(name=contest.title)
        
    #for each problem
    for problem in problems:
        print "Add problem to problem list:"
        print problem.title
        p = Problem.objects.create(title=problem.title, 
                              description=problem.description,
                              input_description=problem.input_description,
                              output_description=problem.output_description,
                              samples=problem.samples,
                              test_case_id=problem.test_case_id,
                              hint=problem.hint,
                              created_by=problem.created_by,
                              time_limit=problem.time_limit,
                              memory_limit=problem.memory_limit,
                              visible = False,
                              difficulty = 0,
                              source = contest.title)
        p.tags.add(tag)
    return