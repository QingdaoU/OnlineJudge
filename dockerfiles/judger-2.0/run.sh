#!/usr/bin/env bash
python -m compileall /var/judger/code
exec supervisord