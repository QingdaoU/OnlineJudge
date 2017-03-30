#!/bin/bash

#判断是否有root权限
if [ `whoami` != "root" ];then
	echo "请用root权限运行此脚本"
	exit 0
fi

# 设置MYSQL密码和RPC_TOKEN
echo -n "请设置MYSQL密码(直接换行默认your_password):" 
read MYSQL_PASSWORD

if  [ ! -n "$MYSQL_PASSWORD" ] ;then
	MYSQL_PASSWORD="your_password"
fi
sed -i "s/{YOUR_PASSWORD}/$MYSQL_PASSWORD/g" ./dockerfiles/oj_web_server/docker-compose.example.yml
cp ./dockerfiles/oj_web_server/docker-compose.example.yml ./dockerfiles/oj_web_server/docker-compose.yml


echo -n "请设置rpc_token(直接换行使用your_token):"
read RPC_TOKEN
if  [ ! -n "$RPC_TOKEN" ] ;then
	RPC_TOKEN="your_token"
fi
sed -i "s/{YOUR_PASSWORD}/$RPC_TOKEN/g" ./dockerfiles/judger/docker-compose.example.yml 
cp ./dockerfiles/judger/docker-compose.example.yml ./dockerfiles/judger/docker-compose.yml

#检查更新，并安装必要程序
apt-get update
apt-get upgrate
apt-get -y install git curl python-pip vim nginx docker.io docker-compose

#  我们使用下面的文件夹进行映射
#    /home/data/mysql MySQL 的数据文件
#    /home/data/redis Redis 的持久化文件
#    /home/test_case 上传的测试用例
#    /home/log 各种日志
#    /home/upload 上传的图片等
mkdir -p /home/OJ/data/mysql /home/OJ/data/redis /home/OJ/test_case /home/OJ/log /home/OJ/upload





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

result1=$(docker images | grep mysql)
result2=$(docker images | grep redis)
result3=$(docker images | grep nginx)
result4=$(docker images | grep oj_web_server)

if [[ "$result1" == "" ]] || [[ "$result2" == "" ]] || [[ "$result3" == "" ]] || [[ "$result4" == "" ]]
then
	docker pull registry.cn-hangzhou.aliyuncs.com/xudianc/redis
	docker tag registry.cn-hangzhou.aliyuncs.com/xudianc/redis redis
	docker pull registry.cn-hangzhou.aliyuncs.com/xudianc/mysql
	docker tag registry.cn-hangzhou.aliyuncs.com/xudianc/mysql mysql
	docker pull registry.cn-hangzhou.aliyuncs.com/xudianc/nginx
	docker tag registry.cn-hangzhou.aliyuncs.com/xudianc/nginx nginx
	docker pull registry.cn-hangzhou.aliyuncs.com/xudianc/oj_web_server
	docker pull registry.cn-hangzhou.aliyuncs.com/xudianc/judger
	docker tag registry.cn-hangzhou.aliyuncs.com/xudianc/oj_web_server qduoj/oj_web_server
	docker tag registry.cn-hangzhou.aliyuncs.com/xudianc/judger qduoj/judger

	result1=$(docker images | grep mysql)
	result2=$(docker images | grep redis)
	result3=$(docker images | grep nginx)
	result4=$(docker images | grep oj_web_server)
	if [[ "$result1" == "" ]] || [[ "$result2" == "" ]] || [[ "$result3" == "" ]] || [[ "$result4" == "" ]]
	then
		echo "网络连接错误，请检查网络后重试"
		exit 1

	fi
fi

# 将代码拷贝到/home/OJ/OnlineJudge
cp -R  ../ /home/OJ/
cd /home/OJ/OnlineJudge

# 配置NGINX
cat ./dockerfiles/oj_web_server/oj.example.conf > /etc/nginx/sites-enabled/default
service nginx restart


# 启动容器
docker-compose -f dockerfiles/oj_web_server/docker-compose.yml up -d

for ((i=10;i>0;i--))
do
	echo -n "$i秒后继续执行 "
	for ((j=0;j<=i;j++))
	do
		echo -n "."
	done
	echo ""
	sleep 1s
done
echo "继续执行中"
CONTAINER_ID=`docker ps -a|grep oj_web_server`
CONTAINER_ID=${CONTAINER_ID%% *}

docker exec -i -t $CONTAINER_ID "_shell/init.sh"
docker restart $CONTAINER_ID

docker-compose -f dockerfiles/judger/docker-compose.yml up -d


CONTAINER_ID=`docker ps -a|grep judger`
CONTAINER_ID=${CONTAINER_ID%% *}

JUDGER_ADDR=`docker inspect --format='{{.NetworkSettings.Networks.bridge.IPAddress}}' $CONTAINER_ID`


clear

echo "安装完成"
echo "请转到http://localhost/ 登录admin，并完成以下配置"
echo -n "OJ管理员帐号:	" 
echo -e "\033[41;33;1mroot\033[0m"
echo -n "OJ管理员密码:	" 
echo -e "\033[41;33;1mpassword\033[0m"
echo -n "判题机IP: 	"  
echo -e "\033[41;33;1m$JUDGER_ADDR\033[0m"
echo -n "判题机TOKEN: 	"  
echo -e "\033[41;33;1m$RPC_TOKEN\033[0m"
echo -n "判题机PORT: 	"  
echo -e "\033[41;33;1m8080\033[0m"
echo -n "MySQL密码: 	"  
echo -e "\033[41;33;1m$MYSQL_PASSWORD\033[0m"


