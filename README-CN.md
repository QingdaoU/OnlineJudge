# OnlineJudge 2.0

[![Python](https://img.shields.io/badge/python-3.8.0-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-362/)
[![Django](https://img.shields.io/badge/django-3.2.9-blue.svg?style=flat-square)](https://www.djangoproject.com/)
[![Django Rest Framework](https://img.shields.io/badge/django_rest_framework-3.12.0-blue.svg?style=flat-square)](http://www.django-rest-framework.org/)
[![Build Status](https://travis-ci.org/QingdaoU/OnlineJudge.svg?branch=master)](https://travis-ci.org/QingdaoU/OnlineJudge)

> #### 基于 Python 和 Vue 的在线评测系统。 [Demo](https://qduoj.com)

[English Document](README.md)

## 概览

+ 基于 Docker，真正一键部署
+ 前后端分离，模块化编程，微服务
+ ACM/OI 两种比赛模式、实时/非实时评判 任意选择
+ 丰富的可视化图表，一图胜千言
+ 支持 Template Problem，可以添加函数题甚至填空题
+ 更细致的权限划分，超级管理员和普通管理员各司其职
+ 多语言支持：`C`, `C++`, `Java`, `Python2`, `Python3`，题目可以选择使用的语言
+ Markdown & MathJax 支持
+ 比赛用户IP限制 (CIDR ranges)

主要模块均已开源:

+ 后端(Django): [https://github.com/QingdaoU/OnlineJudge](https://github.com/QingdaoU/OnlineJudge)
+ 前端(Vue): [https://github.com/QingdaoU/OnlineJudgeFE](https://github.com/QingdaoU/OnlineJudgeFE)
+ 判题沙箱(Seccomp): [https://github.com/QingdaoU/Judger](https://github.com/QingdaoU/Judger)
+ 判题服务器(对Judger的封装): [https://github.com/QingdaoU/JudgeServer](https://github.com/QingdaoU/JudgeServer)

## 安装

请根据此进行安装:  [https://github.com/QingdaoU/OnlineJudgeDeploy/tree/2.0](https://github.com/QingdaoU/OnlineJudgeDeploy/tree/2.0)

## 文档

[http://opensource.qduoj.com/](http://opensource.qduoj.com/)

## 截图

### OJ前台

![problem-list](https://user-images.githubusercontent.com/20637881/33372506-402022e4-d539-11e7-8e64-6656f8ceb75a.png)

![problem-details](https://user-images.githubusercontent.com/20637881/33372507-4061a782-d539-11e7-8835-076ddae6b529.png)

![statistic-info](https://user-images.githubusercontent.com/20637881/33372508-40a0c6ce-d539-11e7-8d5e-024541b76750.png)

![contest-list](https://user-images.githubusercontent.com/20637881/33372509-40d880dc-d539-11e7-9eba-1f08dcb6b9a0.png)

Rankings 中可以控制图表和菜单的显隐。
![acm-rankings](https://user-images.githubusercontent.com/20637881/33372510-41117f68-d539-11e7-9947-70e60bad3cf2.png)
![oi-rankings](https://user-images.githubusercontent.com/20637881/33372511-41d406fa-d539-11e7-9947-7a2a088785b0.png)

![status](https://user-images.githubusercontent.com/20637881/33372512-420ba240-d539-11e7-8645-594cac4a0b78.png)

![status-details](https://user-images.githubusercontent.com/20637881/33365523-787bd0ea-d523-11e7-953f-dacbf7a506df.png)

![user-home](https://user-images.githubusercontent.com/20637881/33365521-7842d808-d523-11e7-84c1-2e2aa0079f32.png)

### 后台管理

![admin-users](https://user-images.githubusercontent.com/20637881/33372516-42c34fda-d539-11e7-9f4e-5109477f83be.png)

![judge-server](https://user-images.githubusercontent.com/20637881/33372517-42faef9e-d539-11e7-9f17-df9be3583900.png)

![create-problem](https://user-images.githubusercontent.com/20637881/33372513-42472162-d539-11e7-8659-5497bf52dbea.png)

![create-contest](https://user-images.githubusercontent.com/20637881/33372514-428ab922-d539-11e7-8f68-da55dedf3ad3.png)


## 浏览器支持

Modern browsers(chrome, firefox) 和 Internet Explorer 10+.

## 特别感谢

+ 所有为本项目做出贡献的人
+ [heb1c](https://github.com/hebicheng) 同学为我们提供了很多意见和建议

如果您觉得这个项目还不错，就star一下吧 ：)

## 许可

The [MIT](http://opensource.org/licenses/MIT) License
