# coding=utf-8
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s',
                    filename='log/judge.log')

logger = logging
