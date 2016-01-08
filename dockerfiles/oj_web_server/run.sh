#!/usr/bin/env bash
find /code -name "*.pyc" -delete
python -m compileall /code
exec supervisord