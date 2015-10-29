# coding=utf-8
"""
注意：
此文件包含 celery 的部分配置，但是 celery 并不是运行在docker 中的，所以本配置文件中的 redis和 MySQL 的地址就应该是
运行 redis 和 MySQL 的 docker 容器的地址了。怎么获取这个地址见帮助文档。测试用例的路径和源代码路径同理。
"""
import os
# 这个redis 是 celery 使用的，包括存储队列信息还有部分统计信息
redis_config = {
    "host": os.environ.get("REDIS_PORT_6379_TCP_ADDR"),
    "port": 6379,
    "db": 0
}


# 判题的 docker 容器的配置参数
docker_config = {
    "image_name": "judger",
    "docker_path": "docker",
    "shell": True
}


# 测试用例的路径，是主机上的实际路径
test_case_dir = "/root/test_case/"
# 源代码路径，也就是 manage.py 所在的实际路径
source_code_dir = "/root/qduoj/"
# 日志文件夹路径
log_dir = "/root/log/"


# 存储提交信息的数据库，是 celery 使用的，与 oj.settings/local_settings 等区分，那是 web 服务器访问的地址
submission_db = {
    "host": os.environ.get("submission_db_host"),
    "port": 3306,
    "db": "oj_submission",
    "user": "root",
    "password": "root"
}
