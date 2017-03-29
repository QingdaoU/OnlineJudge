#!/bin/bash 

python tools/create_db.py
python manage.py migrate
python manage.py migrate --database=submission
python manage.py initadmin
python tools/release_static.py


