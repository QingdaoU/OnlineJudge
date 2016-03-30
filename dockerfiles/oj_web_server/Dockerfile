FROM python:2.7
ENV PYTHONBUFFERED 1
RUN mkdir -p /code/log /code/test_case /code/upload
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -i http://pypi.douban.com/simple  -r requirements.txt --trusted-host pypi.douban.com
RUN rm /etc/apt/sources.list
ADD sources.list /etc/apt/
RUN curl -sL https://deb.nodesource.com/setup | bash -
RUN apt-get -y install nodejs
ADD gunicorn.conf /etc
ADD supervisord.conf /etc
ADD task_queue.conf /etc
EXPOSE 8080
CMD bash /code/dockerfiles/oj_web_server/run.sh