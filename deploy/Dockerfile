FROM python:3.5
ADD requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /app
CMD python manage.py runserver 0.0.0.0:8085
