# coding=utf-8
import os


redis_config = {
    "host": os.environ.get("REDIS_PORT_6379_TCP_ADDR"),
    "port": 6379,
    "db": 0
}