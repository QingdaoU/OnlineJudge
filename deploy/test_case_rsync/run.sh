#!/usr/bin/env sh

slave_runner()
{
    while true
    do
        rsync -avzP --delete --progress --password-file=/etc/rsync_slave.passwd $RSYNC_USER@$RSYNC_MASTER_ADDR::testcase /test_case >> /log/rsync_slave.log
        sleep 5
    done
}

master_runner()
{
    rsync --daemon --config=/etc/rsyncd.conf
    while true
    do
        sleep 60
    done
}

if [ "$RSYNC_MODE" = "master" ]; then
    if [ ! -f "/etc/rsyncd.passwd" ]; then
        echo "$RSYNC_USER:$RSYNC_PASSWORD" > /etc/rsyncd.passwd
    fi
    chmod 600 /etc/rsyncd.passwd
    master_runner
else
    if [ ! -f "/etc/rsync_slave.passwd" ]; then
        echo "$RSYNC_PASSWORD" > /etc/rsync_slave.passwd
    fi
    chmod 600 /etc/rsync_slave.passwd
    slave_runner
fi
