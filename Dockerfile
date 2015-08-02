FROM python:2.7
ENV PYTHONUNBUFFERED 1
ENV oj_env daocloud
RUN mkdir /var/oj
COPY . /var/oj/
WORKDIR /var/oj/
RUN pip install -r requirements.txt
EXPOSE 8080
RUN mkdir LOG
CMD python manage.py runserver 0.0.0.0:8080
