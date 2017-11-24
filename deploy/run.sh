#!/bin/bash

BASE=/app
DATA=$BASE/data

if [ ! -f "$BASE/oj/custom_settings.py" ]; then
    echo SECRET_KEY=\"$(cat /dev/urandom | head -1 | md5sum | head -c 32)\" >> $BASE/oj/custom_settings.py
fi

mkdir -p $DATA/log $DATA/testcase $DATA/public/upload

cd $BASE

n=0
while [ $n -lt 5 ]
do
    python manage.py migrate --no-input &&
    python manage.py initinstall &&
    break
    n=$(($n+1))
    echo "Failed to migrate, going to retry..."
    sleep 8
done

cp $BASE/deploy/oj.conf /etc/nginx/conf.d/default.conf

chown -R nobody:nogroup $DATA $BASE/dist
exec supervisord -c /app/deploy/supervisor.conf
