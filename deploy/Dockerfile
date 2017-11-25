FROM python:3.6-alpine3.6

ENV OJ_ENV production
RUN apk add --no-cache supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev

ADD deploy/requirements.txt /tmp
RUN printf "https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.6/community/\nhttps://mirrors.tuna.tsinghua.edu.cn/alpine/v3.6/main/" > /etc/apk/repositories && \
    apk add --update --no-cache build-base nginx openssl curl unzip && \
    pip install --no-cache-dir -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    apk del build-base --purge

ADD . /app
WORKDIR /app
RUN curl -L  $(curl -s  https://api.github.com/repos/QingdaoU/OnlineJudgeFE/releases/latest | grep /dist.zip | cut -d '"' -f 4) -o dist.zip && \
    unzip dist.zip && \
    rm dist.zip
CMD sh /app/deploy/run.sh
