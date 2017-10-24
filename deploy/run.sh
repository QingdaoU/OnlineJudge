#!/bin/bash

BASE=/app

if [ ! -f "$BASE/custom_settings.py" ]; then
    echo SECRET_KEY=\"$(cat /dev/urandom | head -1 | md5sum | head -c 32)\" >> /app/oj/custom_settings.py
fi

if [ ! -d "$BASE/log" ]; then
    mkdir -p $BASE/log
fi

cd $BASE
find . -name "*.pyc" -delete

# wait for postgresql start
sleep 5

n=0
while [ $n -lt 3 ]
do
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Can't start server, try again in 3 seconds.."
    sleep 3
    let "n+=1"
    continue
fi
python manage.py initadmin
break
done

if [ $n -eq 3 ]; then
    echo "Can't start server, please check log file for details."
    exit 1
fi

chown -R nobody:nogroup /data/log /data/test_case /data/avatar
exec supervisord -c /app/deploy/supervisor.conf
