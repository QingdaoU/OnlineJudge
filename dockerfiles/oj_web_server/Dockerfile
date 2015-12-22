FROM python:2.7
ENV PYTHONBUFFERED 1
RUN mkdir -p /code/log /code/test_case /code/upload
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -i http://pypi.douban.com/simple  -r requirements.txt --trusted-host pypi.douban.com
EXPOSE 8010
CMD supervisord
