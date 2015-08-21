# coding=utf-8
import redis
import datetime
from rest_framework.views import APIView
from judge.judger.result import result
from judge.judger_controller.settings import redis_config
from utils.shortcuts import success_response
from submission.models import Submission


class QueueLengthMonitorAPIView(APIView):
    def get(self, request):
        r = redis.Redis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
        waiting_number = r.get("judge_queue_length")
        if waiting_number is None:
            waiting_number = 0
        now = datetime.datetime.now()
        return success_response({"time": ":".join([str(now.hour), str(now.minute), str(now.second)]),
                                 "count": waiting_number})