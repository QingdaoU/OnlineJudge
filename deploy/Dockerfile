FROM python:3.6-alpine3.6

ADD requirements.txt /tmp
RUN apk add --no-cache --virtual .build-deps build-base jpeg-dev zlib-dev postgresql-dev && \
    pip install -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    apk del .build-deps --purge

Volume ["/app"]

CMD sh /app/deploy/run.sh
