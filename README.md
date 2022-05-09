# OnlineJudge 2.0

[![Python](https://img.shields.io/badge/python-3.8.0-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-362/)
[![Django](https://img.shields.io/badge/django-3.2.9-blue.svg?style=flat-square)](https://www.djangoproject.com/)
[![Django Rest Framework](https://img.shields.io/badge/django_rest_framework-3.12.0-blue.svg?style=flat-square)](http://www.django-rest-framework.org/)
[![Build Status](https://travis-ci.org/QingdaoU/OnlineJudge.svg?branch=master)](https://travis-ci.org/QingdaoU/OnlineJudge)

> #### An onlinejudge system based on Python and Vue. [Demo](https://qduoj.com)

[中文文档](README-CN.md)

## Overview

+ Based on Docker; One-click deployment
+ Separated backend and frontend; Modular programming; Micro service
+ ACM/OI rule support; realtime/non-realtime rank support
+ Amazing charting and visualization
+ Template-problem support
+ More reasonable permission control
+ Multi-language support: `C`, `C++`, `Java`, `Python2`, `Python3`
+ Markdown & MathJax support
+ Contest participants IP limit(CIDR)

Main modules are available below:

+ Backend(Django): [https://github.com/QingdaoU/OnlineJudge](https://github.com/QingdaoU/OnlineJudge)
+ Frontend(Vue): [https://github.com/QingdaoU/OnlineJudgeFE](https://github.com/QingdaoU/OnlineJudgeFE)
+ Judger Sandbox(Seccomp): [https://github.com/QingdaoU/Judger](https://github.com/QingdaoU/Judger)
+ JudgeServer(A wrapper for Judger): [https://github.com/QingdaoU/JudgeServer](https://github.com/QingdaoU/JudgeServer)

## Installation

Follow me:  [https://github.com/QingdaoU/OnlineJudgeDeploy/tree/2.0](https://github.com/QingdaoU/OnlineJudgeDeploy/tree/2.0)

## Documents

[http://opensource.qduoj.com/](http://opensource.qduoj.com/)

## Screenshots

### Frontend:

![problem-list](https://user-images.githubusercontent.com/20637881/33372506-402022e4-d539-11e7-8e64-6656f8ceb75a.png)

![problem-details](https://user-images.githubusercontent.com/20637881/33372507-4061a782-d539-11e7-8835-076ddae6b529.png)

![statistic-info](https://user-images.githubusercontent.com/20637881/33372508-40a0c6ce-d539-11e7-8d5e-024541b76750.png)

![contest-list](https://user-images.githubusercontent.com/20637881/33372509-40d880dc-d539-11e7-9eba-1f08dcb6b9a0.png)

You can control the menu and chart status in rankings.

![acm-rankings](https://user-images.githubusercontent.com/20637881/33372510-41117f68-d539-11e7-9947-70e60bad3cf2.png)

![oi-rankings](https://user-images.githubusercontent.com/20637881/33372511-41d406fa-d539-11e7-9947-7a2a088785b0.png)

![status](https://user-images.githubusercontent.com/20637881/33372512-420ba240-d539-11e7-8645-594cac4a0b78.png)

![status-details](https://user-images.githubusercontent.com/20637881/33365523-787bd0ea-d523-11e7-953f-dacbf7a506df.png)

![user-home](https://user-images.githubusercontent.com/20637881/33365521-7842d808-d523-11e7-84c1-2e2aa0079f32.png)

### Admin: 

![admin-users](https://user-images.githubusercontent.com/20637881/33372516-42c34fda-d539-11e7-9f4e-5109477f83be.png)

![judge-server](https://user-images.githubusercontent.com/20637881/33372517-42faef9e-d539-11e7-9f17-df9be3583900.png)

![create-problem](https://user-images.githubusercontent.com/20637881/33372513-42472162-d539-11e7-8659-5497bf52dbea.png)

![create-contest](https://user-images.githubusercontent.com/20637881/33372514-428ab922-d539-11e7-8f68-da55dedf3ad3.png)

## Browser Support

Modern browsers(chrome, firefox) and Internet Explorer 10+.

## Thanks

+ I'd appreciate a star if you find this helpful.
+ Thanks to everyone that contributes to this project.
+ Special thanks to [heb1c](https://github.com/hebicheng), who has given us a lot of suggestions.

## License

[MIT](http://opensource.org/licenses/MIT)
