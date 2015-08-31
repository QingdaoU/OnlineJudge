# coding=utf-8
# 这个redis 是 celery 使用的，包括存储队列信息还有部分统计信息
redis_config = {
    "host": "121.42.32.129",
    "port": 6379,
    "db": 0
}


# 判题的 docker 容器的配置参数
docker_config = {
    "image_name": "5453975e94c4",
    "docker_path": "docker",
    "shell": True
}


# 测试用例的路径，是主机上的实际路径
test_case_dir = "/var/mnt/source/test_case/"
# 源代码路径，也就是 manage.py 所在的实际路径
source_code_dir = "/var/mnt/source/OnlineJudge/"


# 存储提交信息的数据库，是 celery 使用的，与 oj.settings/local_settings 等区分，那是 web 服务器访问的地址
submission_db = {
    "host": "127.0.0.1",
    "port": 3306,
    "db": "oj_submission",
    "user": "root",
    "password": "root"
}