FROM ubuntu:14.04
ENV DEBIAN_FRONTEND noninteractive
RUN rm /etc/apt/sources.list
COPY sources.list /etc/apt/
RUN apt-get update
RUN apt-get -y install software-properties-common python-software-properties python python-dev gcc g++ git libtool python-pip libseccomp-dev
RUN add-apt-repository -y ppa:webupd8team/java
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
RUN apt-get update
RUN apt-get install -y oracle-java7-installer
RUN cd /tmp && git clone https://github.com/QingdaoU/Judger && cd Judger && python setup.py install
RUN mkdir -p /var/judger/run/ && mkdir /var/judger/test_case/ && mkdir /var/judger/code/
RUN chmod -R 777 /var/judger/run/
COPY policy /var/judger/run/
COPY supervisord.conf /etc
RUN pip install supervisor
WORKDIR /var/judger/code/judge/
EXPOSE 8080
CMD bash /var/judger/code/dockerfiles/judger/run.sh