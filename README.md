# OnlineJudge 2.0

[![vue](https://img.shields.io/badge/python-3.6.2-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-362/)
[![vuex](https://img.shields.io/badge/django-1.11.4-blue.svg?style=flat-square)](https://www.djangoproject.com/)
[![echarts](https://img.shields.io/badge/django_rest_framework-3.4.0-blue.svg?style=flat-square)](http://www.django-rest-framework.org/)
[![Build Status](https://travis-ci.org/QingdaoU/OnlineJudge.svg?branch=2.0)](https://travis-ci.org/QingdaoU/OnlineJudge)

> ### 基于Python和Vue的在线评测系统。[Demo](http://v2.qduoj.com)

## 概览

+ 基于docker，真正一键部署
+ 前后端分离，模块化编程，微服务
+ ACM/OI 两种比赛模式、实时/非实时评判 任意选择
+ 丰富的可视化图表，一图胜千言
+ 支持Template Problem，可以添加函数题甚至填空题
+ 更细致的权限划分，超级管理员和普通管理员各司其职
+ 多语言支持：`C`, `C++`, `Java`, `Python`，题目可以选择使用的语言
+ Markdown & MathJax支持
+ 比赛用户IP限制(CIDR ranges)


主要模块均已开源:

+ 后端(Django): [https://github.com/QingdaoU/OnlineJudge](https://github.com/QingdaoU/OnlineJudge)
+ 前端(Vue): [https://github.com/QingdaoU/OnlineJudgeFE](https://github.com/QingdaoU/OnlineJudgeFE)
+ 判题服务器(Judger): [https://github.com/QingdaoU/JudgeServer](https://github.com/QingdaoU/JudgeServer)
+ VirtualJuge(Golang): 正在开发中..

## 安装

文档:  [https://github.com/QingdaoU/OnlineJudgeDeploy/tree/2.0](https://github.com/QingdaoU/OnlineJudgeDeploy/tree/2.0)

## 截图

### OJ前台

![problem-list](https://user-images.githubusercontent.com/20637881/33365524-78b74d3c-d523-11e7-939e-84123cd94ffa.png)

![problem-detail](https://user-images.githubusercontent.com/20637881/33365526-78f0c742-d523-11e7-8b0e-93120639d05c.png)
![chart-detail](https://user-images.githubusercontent.com/20637881/33365527-792de76c-d523-11e7-89ac-0e8b3ae59a73.png)

![status](https://user-images.githubusercontent.com/20637881/33365519-7809982c-d523-11e7-9bc2-3e8b8a016ffd.png)

![status-details](https://user-images.githubusercontent.com/20637881/33365523-787bd0ea-d523-11e7-953f-dacbf7a506df.png)

![user-home](https://user-images.githubusercontent.com/20637881/33365521-7842d808-d523-11e7-84c1-2e2aa0079f32.png)

![contest-list](https://user-images.githubusercontent.com/20637881/33365528-7966a16a-d523-11e7-8834-4be5e0f9471d.png)

Rankings 中可以控制图表和菜单的显隐
![oi rank](https://user-images.githubusercontent.com/20637881/33366292-c657f904-d525-11e7-947e-c5a4b7606439.png)
![acm-rank](https://user-images.githubusercontent.com/20637881/33366293-c6c62a5a-d525-11e7-9e37-2a354cda5310.png)


### 后台管理

![admin-user](https://user-images.githubusercontent.com/20637881/33365529-79b4513a-d523-11e7-97e4-5dc0144c3101.png)

![judge_server](https://user-images.githubusercontent.com/20637881/33365530-79ef72d8-d523-11e7-8094-3eb50ec74ad8.png)

![create-problem](https://user-images.githubusercontent.com/20637881/33365531-7a2a46ba-d523-11e7-9348-ce6f7a36b37d.png)

![create-contest](https://user-images.githubusercontent.com/20637881/33365532-7a64026a-d523-11e7-965a-4ead1082b124.png)

## 特别感谢

+ [heb1c]()同学为我们提供了很多意见和建议

## 许可

[SATA](https://github.com/zTrix/sata-license)