#!/usr/bin/env bash
if [ ! -f "/code/oj/secret_key.py" ]; then
 echo "SECRET_KEY=\"`cat /dev/urandom | head -1 | md5sum | head -c 32`\"" >> /code/oj/secret_key.py
fi

ca_base_dir="/code/ssl"
if [ ! -f "$ca_base_dir/server.key" ]; then
    openssl req -x509 -newkey rsa:2048 -keyout "$ca_base_dir/server.key" -out "$ca_base_dir/server.crt" -days 1000 \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=Beijing OnlineJudge Technology Co., Ltd./OU=Service Infrastructure Department/CN=`hostname`" -nodes
fi

find /code -name "*.pyc" -delete
# python -m compileall /code
chown -R nobody:nogroup /code/log /code/test_case /code/upload /code/ssl
cd /code
n=0
until [ $n -ge 5 ]
do
    python tools/create_db.py &&
    python manage.py migrate --no-input && 
    python manage.py migrate --database=submission --no-input &&
    python manage.py initadmin && break
    n=$(($n+1))
    sleep 8
done
exec supervisord -c /code/dockerfiles/oj_web_server/supervisord.conf
