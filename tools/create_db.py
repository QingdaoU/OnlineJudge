# coding=utf-8
import os
import time
import MySQLdb

conn = MySQLdb.connect(host="oj_mysql",
                       user=os.environ["MYSQL_ENV_MYSQL_USER"],
                       passwd=os.environ["MYSQL_ENV_MYSQL_ROOT_PASSWORD"])
conn.cursor().execute("create database if not exists oj default character set utf8;")
conn.cursor().execute("create database if not exists oj_submission default character set utf8;")
print "Create database successfully"
