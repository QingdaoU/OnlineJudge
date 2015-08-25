#!/usr/bin/env bash
coverage run --source='.' manage.py test
test_result=$?
if [ "$test_result" -eq 0 ];then
    coverage html
    open htmlcov/index.html
fi
