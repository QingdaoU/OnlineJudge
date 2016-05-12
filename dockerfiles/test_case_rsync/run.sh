#!/usr/bin/env bash
if [ "$RSYNC_MODE" = "master" ]; then
    if [ ! -f "/etc/rsyncd/rsync_master.passwd" ]; then
        mkdir /etc/rsyncd
        (echo "ojrsync:" && cat /OnlineJudge/dockerfiles/test_case_rsync/rsyncd.passwd) | tr -d "\n" > /etc/rsyncd/rsyncd.passwd
    fi
    chmod 600 /etc/rsyncd/rsyncd.passwd
    rsync --daemon --config=/OnlineJudge/dockerfiles/test_case_rsync/rsyncd.conf
else
    chmod 600 /OnlineJudge/dockerfiles/test_case_rsync/rsyncd.passwd
    /bin/bash /OnlineJudge/dockerfiles/test_case_rsync/rsyncd_slave.sh
fi
while true
do
    sleep 100
done
