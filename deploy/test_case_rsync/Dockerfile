FROM alpine:3.6

RUN apk add --update --no-cache rsync

ADD ./run.sh /tmp/run.sh
ADD ./rsyncd.conf /etc/rsyncd.conf

CMD /bin/sh /tmp/run.sh