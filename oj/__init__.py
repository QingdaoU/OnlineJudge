"""
   ___         _  _                  __              _                _                         _
  /___\ _ __  | |(_) _ __    ___     \ \  _   _   __| |  __ _   ___  | |__   _   _    __ _   __| | _   _
 //  //| '_ \ | || || '_ \  / _ \     \ \| | | | / _` | / _` | / _ \ | '_ \ | | | |  / _` | / _` || | | |
/ \_// | | | || || || | | ||  __/  /\_/ /| |_| || (_| || (_| ||  __/ | |_) || |_| | | (_| || (_| || |_| |
\___/  |_| |_||_||_||_| |_| \___|  \___/  \__,_| \__,_| \__, | \___| |_.__/  \__, |  \__, | \__,_| \__,_|
                                                        |___/                |___/      |_|
https://github.com/QingdaoU/OnlineJudge
"""
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app