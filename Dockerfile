FROM ubuntu
RUN apt-get update
RUN apt-get -y install software-properties-common python-software-properties
RUN apt-get -y install python
RUN apt-get -y install python-pip
ENV PYTHONUNBUFFERED 1
ENV oj_env daocloud
RUN mkdir /var/oj
COPY . /var/oj/
WORKDIR /var/oj/
RUN pip install -r requirements.txt
EXPOSE 8080
RUN mkdir LOG
CMD python manage.py runserver 8080
