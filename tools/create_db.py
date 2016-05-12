# coding=utf-8
import os
import time
import MySQLdb
"""
docker-compose启动的时候是并行启动的,可能执行本脚本的时候MySQL还没启动完
"""
i = 3
while i:
    try:
        conn = MySQLdb.connect(host=os.environ["MYSQL_PORT_3306_TCP_ADDR"],
                               user=os.environ["MYSQL_ENV_MYSQL_USER"],
                               passwd=os.environ["MYSQL_ENV_MYSQL_ROOT_PASSWORD"])
        conn.cursor().execute("create database if not exists oj default character set utf8;")
        conn.cursor().execute("create database if not exists oj_submission default character set utf8;")
        print "Create database successfully"
        exit(0)
    except Exception as e:
        print "Failed to create database, error: " + str(e) + ", will retry in 3 seconds"
        i -= 1
        time.sleep(3)
print "Failed to create database"
exit(1)
