#!/bin/bash

APP=/app
DATA=/data

if [ ! -f "$APP/oj/custom_settings.py" ]; then
    echo SECRET_KEY=\"$(cat /dev/urandom | head -1 | md5sum | head -c 32)\" >> $APP/oj/custom_settings.py
fi

mkdir -p $DATA/log $DATA/ssl $DATA/test_case $DATA/public/upload $DATA/public/avatar

SSL="$DATA/ssl"
if [ ! -f "$SSL/server.key" ]; then
    openssl req -x509 -newkey rsa:2048 -keyout "$SSL/server.key" -out "$SSL/server.crt" -days 1000 \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=Beijing OnlineJudge Technology Co., Ltd./OU=Service Infrastructure Department/CN=`hostname`" -nodes
fi

cd $APP

n=0
while [ $n -lt 5 ]
do
    python manage.py migrate --no-input &&
    python manage.py inituser --username=root --password=rootroot --action=create_super_admin &&
    break
    n=$(($n+1))
    echo "Failed to migrate, going to retry..."
    sleep 8
done

echo "from options.options import SysOptions; SysOptions.judge_server_token='$JUDGE_SERVER_TOKEN'" | python manage.py shell || exit 1

cp data/public/avatar/default.png /data/public/avatar
chown -R nobody:nogroup $DATA $APP/dist
exec supervisord -c /app/deploy/supervisord.conf
