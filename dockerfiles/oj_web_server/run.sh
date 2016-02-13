#!/usr/bin/env bash
find /code -name "*.pyc" -delete
python -m compileall /code
chown -R nobody:nogroup /code/log /code/test_case /code/upload
exec supervisord