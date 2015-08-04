#!/usr/bin/env bash
coverage run --source='.' manage.py test
nose html
open htmlcov/index.html
