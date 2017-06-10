FROM ubuntu:16.04
ENV PYTHONBUFFERED 1
RUN apt-get update && apt-get install -y nginx python-pip libmysqlclient-dev curl nodejs
RUN curl -sL https://deb.nodesource.com/setup | bash -
RUN apt-get install nodejs
ADD . /code
WORKDIR /code
RUN pip install -i https://pypi.douban.com/simple -r dockerfiles/oj_web_server/requirements.txt
RUN python tools/release_static.py
EXPOSE 80
CMD bash /code/dockerfiles/oj_web_server/run.sh
