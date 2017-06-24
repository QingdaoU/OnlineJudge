FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -y install software-properties-common python-software-properties python python-dev gcc g++ git libtool python-pip libseccomp-dev
RUN add-apt-repository -y ppa:webupd8team/java && echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
RUN apt-get update && apt-get install -y oracle-java8-installer
RUN cd /tmp && git clone -b master https://github.com/QingdaoU/Judger && cd Judger && python setup.py install
RUN mkdir -p /var/judger/run/ && mkdir /var/judger/test_case/ && mkdir /var/judger/code/
RUN chmod -R 777 /var/judger/run/
COPY dockerfiles/judger/policy /var/judger/run/
COPY dockerfiles/judger/supervisord.conf /etc
RUN pip install supervisor
ADD . /var/judger/code
WORKDIR /var/judger/code/judge/
EXPOSE 8080
CMD bash /var/judger/code/dockerfiles/judger/run.sh
