#!/usr/bin/env bash
while true
do
    rsync -avz --delete --progress --password-file=/OnlineJudge/dockerfiles/test_case_rsync/rsyncd.passwd ojrsync@$RSYNC_MASTER_ADDR::testcase /OnlineJudge/test_case >> /OnlineJudge/log/rsync_slave.log
    sleep 5
done
