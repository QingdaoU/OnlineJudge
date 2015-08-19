# coding=utf-8
import datetime
import redis
import MySQLdb
import subprocess
from ..judger.result import result
from ..judger_controller.celery import app
from settings import docker_config, source_code_dir, test_case_dir, submission_db, redis_config


@app.task
def judge(submission_id, time_limit, memory_limit, test_case_id):
    # 先更新判题队列长度
    r = redis.StrictRedis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
    length = r.incr("queue_length")
    now = datetime.datetime.now()
    # 使用hash key是今天的日期 value 的 key 是当前时分秒 12:02:03 value 是队列长度
    r.hset(str(datetime.date.today()), ":".join([str(now.hour), str(now.minute), str(now.second)]), length)
    try:
        command = "%s run -t -i --privileged --rm=true " \
                  "-v %s:/var/judger/test_case/ " \
                  "-v %s:/var/judger/code/ " \
                  "%s " \
                  "python judge/judger/run.py " \
                  "--solution_id %s --time_limit %s --memory_limit %s --test_case_id %s" % \
                  (docker_config["docker_path"],
                   test_case_dir,
                   source_code_dir,
                   docker_config["image_name"],
                   submission_id, str(time_limit), str(memory_limit), test_case_id)
        subprocess.call(command, shell=docker_config["shell"])
    except Exception as e:
        print e
        conn = MySQLdb.connect(db=submission_db["db"],
                               user=submission_db["user"],
                               passwd=submission_db["password"],
                               host=submission_db["host"],
                               port=submission_db["port"],
                               character="utf8")

        cur = conn.cursor()
        cur.execute("update submission set result=%s, info=%s where id=%s",
                    (result["system_error"], str(e), submission_id))
        conn.commit()
        conn.close()
    r.decr("queue_length")
    now = datetime.datetime.now()
    # 使用hash key是今天的日期 value 的 key 是当前时分秒 12:02:03 value 是队列长度
    r.hset(str(datetime.date.today()), ":".join([str(now.hour), str(now.minute), str(now.second)]), length)
