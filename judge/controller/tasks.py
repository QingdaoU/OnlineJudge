# coding=utf-8
from __future__ import absolute_import
from judge.controller.celery import app
import subprocess32 as subprocess


@app.task
def judge(solution_id, time_limit, memory_limit, test_case_id):
    subprocess.call("/usr/bin/docker run -t -i --privileged -v /var/test_case/:/var/judger/test_case/ "
                    "-v /var/code/:/var/judger/code/ judger python judge/judger/run.py "
                    "--solution_id %s --time_limit %s --memory_limit %s --test_case_id %s" %
                    (solution_id, str(time_limit), str(memory_limit), test_case_id),
                    timeout=(time_limit / 100) * 20)
