# coding=utf-8
import json
import redis
import MySQLdb
import subprocess
from ..judger.result import result
from ..judger_controller.celery import app
from settings import docker_config, source_code_dir, test_case_dir, log_dir, submission_db, redis_config


@app.task
def judge(submission_id, time_limit, memory_limit, test_case_id):
    try:
        command = "%s run --privileged --rm " \
                  "--link mysql " \
                  "-v %s:/var/judger/test_case/ " \
                  "-v %s:/var/judger/code/ " \
                  "-v %s:/var/judger/code/log/ " \
                  "%s " \
                  "python judge/judger/run.py " \
                  "--solution_id %s --time_limit %s --memory_limit %s --test_case_id %s" % \
                  (docker_config["docker_path"],
                   test_case_dir,
                   source_code_dir,
                   log_dir,
                   docker_config["image_name"],
                   submission_id, str(time_limit), str(memory_limit), test_case_id)
        subprocess.call(command, shell=docker_config["shell"])
    except Exception as e:
        conn = MySQLdb.connect(db=submission_db["db"],
                               user=submission_db["user"],
                               passwd=submission_db["password"],
                               host=submission_db["host"],
                               port=submission_db["port"],
                               charset="utf8")

        cur = conn.cursor()
        cur.execute("update submission set result=%s, info=%s where id=%s",
                    (result["system_error"], str(e), submission_id))
        conn.commit()
        conn.close()
    r = redis.Redis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
    r.decr("judge_queue_length")
    r.lpush("queue", submission_id)
