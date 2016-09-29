FROM mysql:latest
RUN printf "\n[mysqld]\nserver-id=1\nlog-bin=binlog\nperformance_schema=OFF\ntable_definition_cache=400\ntable_open_cache=256" >> /etc/mysql/my.cnf
