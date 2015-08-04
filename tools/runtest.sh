#!/usr/bin/env bash
coverage run --source='.' manage.py test
coverage html
open htmlcov/index.html
