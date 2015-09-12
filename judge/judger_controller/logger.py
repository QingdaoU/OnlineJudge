# coding=utf-8
import logging

# 此处的 celery 代码如果在 docker 中运行，需要将filename 修改为映射路径
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s',
                    filename='/var/log/judge.log')

logger = logging
