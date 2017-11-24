FROM python:3.6-alpine3.6

ENV OJ_ENV production
RUN apk add --no-cache supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev

ADD deploy/requirements.txt /tmp
RUN apk add --update --no-cache build-base nginx openssl  && \
    pip install --no-cache-dir -r /tmp/requirements.txt -i https://pypi.doubanio.com/simple && \
    apk del build-base --purge

ADD . /app
CMD sh /app/deploy/run.sh
