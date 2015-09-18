# coding=utf-8
import os
import json

os.system("docker rm -f redis")
os.system("docker rm -f mysql")
os.system("docker rm -f oj_web_server")

if os.system("docker run --name mysql -v /root/data:/var/lib/mysql -v /root/data/my.cnf:/etc/my.cnf -e MYSQL_ROOT_PASSWORD=root  -d mysql/mysql-server:latest"):
    print "Error start mysql"
    exit()

if os.system("docker run --name redis -d redis"):
    print "Error start redis"
    exit()

if os.system("docker run --name oj_web_server -e oj_env=server -v /root/qduoj:/code -v /root/test_case:/code/test_case -v /root/log:/code/log -v /root/upload:/code/upload -v /root/qduoj/dockerfiles/oj_web_server/supervisord.conf:/etc/supervisord.conf -v /root/qduoj/dockerfiles/oj_web_server/gunicorn.conf:/etc/gunicorn.conf -v /root/qduoj/dockerfiles/oj_web_server/mq.conf:/etc/mq.conf -d -p 127.0.0.1:8080:8080 --link mysql --link=redis oj_web_server"):
    print "Erro start oj_web_server"
    exit()

inspect_redis = json.loads(os.popen("docker inspect redis").read())

if not inspect_redis:
    print "Error when inspect redis ip"
    exit()

redis_ip = inspect_redis[0]["NetworkSettings"]["IPAddress"]
print "redis ip ", redis_ip


inspect_mysql = json.loads(os.popen("docker inspect mysql").read())
if not inspect_mysql:
    print "Error when inspect mysql ip"
    exit()

mysql_ip = inspect_mysql[0]["NetworkSettings"]["IPAddress"]
print "mysql ip ", mysql_ip


f = open("/etc/profile", "r")
content = ""
for line in f.readlines():
    if line.startswith("export REDIS_PORT_6379_TCP_ADDR"):
        content += ("\nexport REDIS_PORT_6379_TCP_ADDR=" + redis_ip + "\n")
    elif line.startswith("export submission_db_host"):
        content += ("\nexport submission_db_host=" + mysql_ip + "\n")
    else:
        content += line

f.close()


f = open("/etc/profile", "w")
f.write(content)
f.close()

print "Please run source /etc/profile"

