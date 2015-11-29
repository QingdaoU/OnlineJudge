# coding=utf-8
import json

from celery import shared_task
from rpc_client import TimeoutServerProxy

from judge.result import result
from submission.models import Submission


@shared_task
def create_judge_task(submission_id, code, language_code, time_limit, memory_limit, test_case_id):
    submission = Submission.objects.get(id=submission_id)
    try:
        s = TimeoutServerProxy('http://121.42.198.156:8080', timeout=20)
        data = s.run(submission_id, language_code, code, time_limit, memory_limit, test_case_id)
        print data
        # 编译错误
        if data["code"] == 1:
            submission.result = result["compile_error"]
            submission.info = data["data"]["error"]
        # system error
        elif data["code"] == 2:
            submission.result = result["system_error"]
            submission.info = data["data"]["error"]
        elif data["code"] == 0:
            submission.result = data["data"]["result"]
            submission.info = json.dumps(data["data"]["info"])
            submission.accepted_answer_time = data["data"]["accepted_answer_time"]
    except Exception as e:
        submission.result = result["system_error"]
        submission.info = str(e)
    finally:
        submission.save()
