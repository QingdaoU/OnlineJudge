# coding=utf-8
import logging
import redis
from judge.judger_controller.settings import redis_config
from judge.judger.result import result
from submission.models import Submission
from problem.models import Problem

logger = logging.getLogger("app_info")


class MessageQueue(object):
    def __init__(self):
        self.conn = redis.StrictRedis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
        self.queue = 'queue'

    def listen_task(self):
        while True:
            submission_id = self.conn.blpop(self.queue, 0)[1]
            logger.debug("receive submission_id: " + submission_id)
            try:
                submission = Submission.objects.get(id=submission_id)
            except Submission.DoesNotExist:
                logger.warning("Submission does not exist, submission_id: " + submission_id)
                pass

            if submission.result == result["accepted"]:
                # 更新题目的 ac 计数器
                try:
                    problem = Problem.objects.get(id=submission.problem_id)
                    problem.total_accepted_number += 1
                    problem.save()
                except Problem.DoesNotExist:
                    logger.warning("Submission problem does not exist, submission_id: " + submission_id)
                    pass


logger.debug("Start message queue")
MessageQueue().listen_task()
