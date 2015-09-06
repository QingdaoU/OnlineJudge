import django
from contest.models import *
from problem.models import *
from submission.models import Submission

import redis

from judge.judger_controller.tasks import judge
from judge.judger_controller.settings import redis_config

django.setup()


def rejudge(submission):
    # for submission in submission:
    #   submission_id = submission.id
    #  try:
    #     command = "%s run -t -i --privileged --rm=true " \
    #              "-v %s:/var/judger/test_case/ " \
    #             "-v %s:/var/judger/code/ " \
    #            "%s " \
    #           "python judge/judger/run.py " \
    #          "--solution_id %s --time_limit %s --memory_limit %s --test_case_id %s" % \
    #         (docker_config["docker_path"],
    #         test_case_dir,
    #        source_code_dir,
    #       docker_config["image_name"],
    #      submission_id, str(time_limit), str(memory_limit), test_case_id)
    # subprocess.call(command, shell=docker_config["shell"])
    # except Exception as e:
    #     print e
    return


def easy_rejudge(submissions, map_table, user_id, contest_id=None):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        print "User.DoesNotExist!"
        return
    problemDict = {}
    for oldSubmission in submission:
        problem_id = map_table[oldSubmission.problem_id]

        if problem_id in problemDict:
            problem = problemDict[problem_id]
        else:
            try:
                p = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                print " Problem.DoesNotExist!" + str(problem_id)
                continue
            problem = p
            problemDict[problem_id] = p

        submission = Submission.objects.create(
            user_id=user_id,
            language=oldSubmission.language,
            code=oldSubmission.code,
            contest_id=contest_id,
            problem_id=problem_id,
            originResult=oldSubmission.result
        )
        try:
            judge.delay(submission.id, problem.time_limit, problem.memory_limit, problem.test_case_id)
        except Exception:
            print "error!"
            continue
            
        r = redis.Redis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
        r.incr("judge_queue_length")

    return

