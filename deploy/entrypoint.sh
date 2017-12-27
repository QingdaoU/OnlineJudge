#!/bin/sh

APP=/app
DATA=/data

mkdir -p $DATA/log $DATA/ssl $DATA/test_case $DATA/public/upload $DATA/public/avatar $DATA/public/website

if [ ! -f "$APP/oj/custom_settings.py" ]; then
    echo SECRET_KEY=\"$(cat /dev/urandom | head -1 | md5sum | head -c 32)\" >> $APP/oj/custom_settings.py
fi

if [ ! -f "$DATA/public/avatar/default.png" ]; then
    cp data/public/avatar/default.png $DATA/public/avatar
fi

if [ ! -f "$DATA/public/website/favicon.ico" ]; then
    cp data/public/website/favicon.ico $DATA/public/website
fi

SSL="$DATA/ssl"
if [ ! -f "$SSL/server.key" ]; then
    openssl req -x509 -newkey rsa:2048 -keyout "$SSL/server.key" -out "$SSL/server.crt" -days 1000 \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=Beijing OnlineJudge Technology Co., Ltd./OU=Service Infrastructure Department/CN=`hostname`" -nodes
fi

cd $APP/deploy/nginx
ln -sf locations.conf https_locations.conf
if [ -z "$FORCE_HTTPS" ]; then
    ln -sf locations.conf http_locations.conf
else
    ln -sf https_redirect.conf http_locations.conf
fi

cd $APP/dist
if [ ! -z "$STATIC_CDN_HOST" ]; then
    find . -name index.html -exec sed -i "s/link href=\/static/link href=\/\/$STATIC_CDN_HOST\/static/g" {} \;
    find . -name index.html -exec sed -i "s/script type=text\/javascript src=\/static/script type=text\/javascript src=\/\/$STATIC_CDN_HOST\/static/g" {} \;
fi

cd $APP

n=0
while [ $n -lt 5 ]
do
    python manage.py migrate --no-input &&
    python manage.py inituser --username=root --password=rootroot --action=create_super_admin &&
    break
    n=$(($n+1))
    echo "Failed to migrate, going to retry..."
    sleep 8
done

echo "from options.options import SysOptions; SysOptions.judge_server_token='$JUDGE_SERVER_TOKEN'" | python manage.py shell || exit 1

chown -R nobody:nogroup $DATA $APP/dist
exec supervisord -c /app/deploy/supervisord.conf