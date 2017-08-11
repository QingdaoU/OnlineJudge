FROM ubuntu:16.04
ENV PYTHONBUFFERED 1
ADD . /code
WORKDIR /code
RUN apt-get update \
    && apt-get install --no-install-recommends -y nginx python-pip \ 
       nodejs libmysqlclient-dev python-setuptools build-essential python-dev \
    && pip install -i https://pypi.douban.com/simple -r dockerfiles/oj_web_server/requirements.txt \
    && apt-get purge -y --auto-remove build-essential python-dev\
    && rm -rf /var/lib/apt/lists/*
RUN python tools/release_static.py
CMD bash /code/dockerfiles/oj_web_server/run.sh
