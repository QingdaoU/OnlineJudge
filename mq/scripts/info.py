# coding=utf-8
import json
import redis
from judge.judger_controller.settings import redis_config
from judge.judger.result import result
from submission.models import Submission
from problem.models import Problem


class MessageQueue(object):
    def __init__(self):
        self.conn = redis.StrictRedis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
        self.queue = 'queue'

    def listen_task(self):
        while True:
            submission_id = self.conn.blpop(self.queue, 0)[1]
            print submission_id
            try:
                submission = Submission.objects.get(id=submission_id)
            except Submission.DoesNotExist:
                print "error 1"
                pass

            if submission.result == result["accepted"]:
                # 更新题目的 ac 计数器
                try:
                    problem = Problem.objects.get(id=submission.problem_id)
                    problem.total_accepted_number += 1
                    problem.save()
                except Problem.DoesNotExist:
                    print "error 2"
                    pass


print "mq running"
MessageQueue().listen_task()
