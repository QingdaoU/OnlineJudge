#!/usr/bin/env python
"""
知识图谱数据导入独立入口
使用方法：docker exec -it onlinejudgedeploy-oj-backend-1 python /code/kg_import.py
"""
import os
import sys
import django

# 确保源码目录在 Python 搜索路径最前面
sys.path.insert(0, '/code')

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # 模拟命令行调用
    execute_from_command_line(['kg_import.py', 'build_knowledge_graph'])
