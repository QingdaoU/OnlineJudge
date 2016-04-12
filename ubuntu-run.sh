#!/bin/bash
service docker start
service nginx start
homepath="/home/"
add1="OnlineJudge/dockerfiles/oj_web_server/"
add2="OnlineJudge/dockerfiles/judger/"
path1=${homepath}${add1}
path2=${homepath}${add2}
cd $path1 && /usr/local/bin/docker-compose up -d
cd $path2 && /usr/local/bin/docker-compose up -d
