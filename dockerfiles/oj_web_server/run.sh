#!/usr/bin/env bash
if [ ! -f "/code/oj/custom_settings.py" ]; then
 cp /code/oj/custom_settings.example.py /code/oj/custom_settings.py
 echo "SECRET_KEY=\"`cat /dev/urandom | head -1 | md5sum | head -c 32`\"" >> /code/oj/custom_settings.py
fi
find /code -name "*.pyc" -delete
python -m compileall /code
chown -R nobody:nogroup /code/log /code/test_case /code/upload
echo "Waiting MySQL and Redis to start"
exec supervisord