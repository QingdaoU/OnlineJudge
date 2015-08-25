@echo off
coverage run --source='.' manage.py test
coverage html
cd htmlcov
index.html
cls
cd..
coverage run --source='.' manage.py test
coverage html
cd htmlcov
index.html

