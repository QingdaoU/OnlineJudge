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

python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Can't start server"
    exit 1
fi
python manage.py initadmin
python manage.py runserver 0.0.0.0:8080
