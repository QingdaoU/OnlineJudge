FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && buildDeps=' \
		software-properties-common \
		python-software-properties \
		python-dev \
		git \
		libtool \
		python-pip \
		libtool \
		libseccomp-dev' \
    && apt-get -y install python gcc g++ python-pkg-resources $buildDeps\
    && add-apt-repository -y ppa:webupd8team/java \
    && echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections \
    && echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections \
    && apt-get update \
    && apt-get install -y oracle-java8-installer \
    && cd /tmp \
    && git clone -b master https://github.com/QingdaoU/Judger \
    && cd Judger \
    && python setup.py install \
    && pip install supervisor \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/judger/run/ \
    && mkdir /var/judger/test_case/ \
    && mkdir /var/judger/code/ \
    && chmod -R 777 /var/judger/run/
COPY dockerfiles/judger/policy /var/judger/run
COPY dockerfiles/judger/supervisord.conf /etc
ADD . /var/judger/code
WORKDIR /var/judger/code/judge/
EXPOSE 8080
CMD bash /var/judger/code/dockerfiles/judger/run.sh

