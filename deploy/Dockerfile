FROM python:3.6-alpine3.6

ENV OJ_ENV production
RUN apk add --no-cache nginx supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev

ADD requirements.txt /tmp
RUN apk add --no-cache build-base  && \
    pip install --no-cache-dir -r /tmp/requirements.txt -i https://pypi.doubanio.com/simple && \
    apk del build-base --purge

VOLUME [ "/app" ]

CMD sh /app/deploy/run.sh
