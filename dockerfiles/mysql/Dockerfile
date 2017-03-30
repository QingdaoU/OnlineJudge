FROM mysql:latest
RUN printf "\n[mysqld]\nserver-id=1\nlog-bin=binlog\nperformance_schema=OFF\ntable_definition_cache=400\ntable_open_cache=256\nbind-address=0.0.0.0" >> /etc/mysql/my.cnf
