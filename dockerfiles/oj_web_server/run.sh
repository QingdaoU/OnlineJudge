#!/usr/bin/env bash
if [ ! -f "/code/oj/custom_settings.py" ]; then
 cp /code/oj/custom_settings.example.py /code/oj/custom_settings.py
 echo "SECRET_KEY=\"`cat /dev/urandom | head -1 | md5sum | head -c 32`\"" >> /code/oj/custom_settings.py
fi
find /code -name "*.pyc" -delete
# python -m compileall /code
chown -R nobody:nogroup /code/log /code/test_case /code/upload
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
