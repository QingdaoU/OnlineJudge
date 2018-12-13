from celery import shared_task

from submission.models import Submission

import os
from django.conf import settings
from contest.models import Contest
from problem.models import Problem
from submission.models import JudgeStatus


@shared_task(time_limit=30)
def similar_task(contest_id):
    problems = Problem.objects.filter(contest_id=contest_id)
    owner = {}
    data_to_write = []

    for problem in problems:
        check_dir = os.path.join(settings.TEST_CASE_DIR, str(problem.id) + "_similar_tmp")
        if not os.path.exists(check_dir):
            os.mkdir(check_dir)
            os.chmod(check_dir, 0o710)

        submissions = Submission.objects.filter(problem_id=problem.id, result=JudgeStatus.ACCEPTED)
        for submission in submissions:
            owner[submission.id] = submission.username
            file_path = os.path.join(check_dir, submission.id)
            f = open(file_path, "w")
            f.write(submission.code)
            f.close()

        output_dir = os.path.join(check_dir, "result")
        check_files = check_dir + "/*"
        os.system(f"/app/sim_c -p -t40 -o {output_dir} {check_files}")
        f = open(output_dir)
        for line in f:
            # xxxx consists for xx % of xxxx material
            if "consists" in line:
                splited_line = line.split()
                sub1 = splited_line[0].split("/")[-1]
                sub2 = splited_line[-2].split("/")[-1]
                if owner[sub1] == owner[sub2]:
                    continue
                sim = splited_line[3]
                to_append = {
                    "problem_id": problem._id,
                    "submission_a": sub1,
                    "user_a": owner[sub1],
                    "submission_b": sub2,
                    "user_b": owner[sub2],
                    "similarity": sim
                }
                data_to_write.append(to_append)
        f.close()

        os.remove(output_dir)
        for submission in submissions:
            owner[submission.id] = submission.username
            file_path = os.path.join(check_dir, submission.id)
            os.remove(file_path)
        os.rmdir(check_dir)

    contest = Contest.objects.get(id=contest_id)
    contest.similarity_check_result = data_to_write
    contest.save()
