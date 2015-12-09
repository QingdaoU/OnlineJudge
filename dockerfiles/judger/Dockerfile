FROM ubuntu:14.04
MAINTAINER virusdefender<qduliyang@outlook.com>
RUN mkdir /var/install/
WORKDIR /var/install/
ENV DEBIAN_FRONTEND noninteractive
RUN rm /etc/apt/sources.list
COPY sources.list /etc/apt/
RUN apt-get update
RUN apt-get -y install software-properties-common python-software-properties
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update
RUN apt-get -y install python gcc g++ rake pkg-config git make autoconf automake libtool python-pip python2.7-mysqldb
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
RUN apt-get install -y oracle-java7-installer
RUN apt-get -y install libseccomp-dev
RUN git clone https://github.com/quark-zju/lrun.git
RUN cd lrun && make install
RUN mkdir -p /var/judger/run/ && mkdir /var/judger/test_case/ && mkdir /var/judger/code/
RUN chmod -R 777 /var/judger/run/
COPY policy /var/judger/run/
WORKDIR /var/judger/code/judge/
CMD python server.py