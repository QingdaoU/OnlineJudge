#!/bin/bash

#判断是否有root权限
if [ `whoami` != "root" ];then
	echo "请用root权限运行此脚本"
	exit 0
fi

exit 0
# 设置MYSQL密码和RPC_TOKEN
echo -n "请设置MYSQL密码:" 
read MYSQL_PASSWORD
sed -i "s/{YOUR_PASSWORD}/$MYSQL_PASSWORD/g" ./dockerfiles/oj_web_server/docker-compose.example.yml
cp ./dockerfiles/oj_web_server/docker-compose.example.yml ./dockerfiles/oj_web_server/docker-compose.yml
echo -n "请设置rpc_token:"
read RPC_TOKEN
sed -i "s/{YOUR_PASSWORD}/$RPC_TOKEN/g" ./dockerfiles/judger/docker-compose.example.yml 
cp ./dockerfiles/judger/docker-compose.example.yml ./dockerfiles/judger/docker-compose.yml

#检查更新，并安装必要程序
apt-get update
apt-get upgrate
apt-get install git curl python-pip vim nginx

#  我们使用下面的文件夹进行映射
#    /home/data/mysql MySQL 的数据文件
#    /home/data/redis Redis 的持久化文件
#    /home/test_case 上传的测试用例
#    /home/log 各种日志
#    /home/upload 上传的图片等
mkdir -p /home/OJ/data/mysql /home/OJ/data/redis /home/OJ/test_case /home/OJ/log /home/OJ/upload

#  安装docker
#    因为国内特殊网络环境，Docker 的安装和使用并不方便，我们使用 DaoCloud 的安装镜像。但是有时候也会出现添加 key 失败的问题，这时候可以使用官方的安装方案。

curl -sSL https://get.daocloud.io/docker | sh

# 安装 docker-compose
pip install docker-compose


##pull 需要的镜像（目前只提供阿里云镜像一种方式）
docker pull registry.aliyuncs.com/v-image/redis
docker tag registry.aliyuncs.com/v-image/redis redis
docker pull registry.aliyuncs.com/v-image/mysql
docker tag registry.aliyuncs.com/v-image/mysql mysql
docker pull registry.aliyuncs.com/v-image/nginx
docker tag registry.aliyuncs.com/v-image/nginx nginx
docker pull registry.aliyuncs.com/v-image/oj_web_server
docker pull registry.aliyuncs.com/v-image/judger
docker tag registry.aliyuncs.com/v-image/oj_web_server qduoj/oj_web_server
docker tag registry.aliyuncs.com/v-image/judger qduoj/judger

# 将代码拷贝到/home/OJ/OnlineJudge
cp -R  ../ /home/OJ/
cd /home/OJ/OnlineJudge

# 配置NGINX
cat ./oj_web_server/oj.conf > /etx/nginx/site-enable/default
service nginx restart

# 启动容器
docker-compose -f dockerfiles/oj_web_server/docker-compose.yml up -d

CONTAINER_ID=`docker ps -a|grep oj_web_server`
CONTAINER_ID=${CONTAINER_ID%% *}

docker exec -i -t $CONTAINER_ID "_shell/init.sh"
docker restart $CONTAINER_ID

docker-compose -f dockerfiles/judger/docker-compose.yml up -d


CONTAINER_ID=`docker ps -a|grep judger`
CONTAINER_ID=${CONTAINER_ID%% *}

docker inspect --format='{{json .NetworkSettings.Networks.bridge.IPAddress}}'
