# coding=utf-8
import redis
import datetime
from rest_framework.views import APIView
from judge.judger.result import result
from utils.shortcuts import success_response
from submission.models import Submission


class QueueLengthMonitorAPIView(APIView):
    def get(self, request):
        waiting_number = Submission.objects.filter(result=result["waiting"]).count()
        now = datetime.datetime.now()
        return success_response({"time": ":".join([str(now.hour), str(now.minute), str(now.second)]),
                                 "count": waiting_number})