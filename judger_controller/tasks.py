# coding=utf-8
from __future__ import absolute_import
from judger_controller.celery import app
import subprocess32 as subprocess


@app.task
def judge(solution_id, time_limit, memory_limit, test_case_id):
    try:
        subprocess.call("docker run -t -i --privileged --rm=true "
                        "-v /Users/virusdefender/Desktop/test_case/:/var/judger/test_case/ "
                        "-v /Users/virusdefender/Desktop/:/var/judger/code/ "
                        "judger "
                        "python judger/run.py "
                        "--solution_id %s --time_limit %s --memory_limit %s --test_case_id %s" %
                        (solution_id, str(time_limit), str(memory_limit), test_case_id),
                        # 如果设置的最长运行时间小于1000毫秒，那么/1000就是0，处理一下这个情况，设置为两秒
                        timeout=(time_limit / 1000 * 3) or 2, shell=True)
    except subprocess.TimeoutExpired:
        print "docker timeout"
