#!/bin/bash
service docker start
service nginx start
base_path="/home/"
web_server_config="${base_path}OnlineJudge/dockerfiles/oj_web_server/"
judger_config="${base_path}OnlineJudge/dockerfiles/judger/"
cd $web_server_config && /usr/local/bin/docker-compose up -d
cd $judger_config && /usr/local/bin/docker-compose up -d
