# OnlineJudge 2.0

[![Python](https://img.shields.io/badge/python-3.6.2-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-362/)
[![Django](https://img.shields.io/badge/django-1.11.4-blue.svg?style=flat-square)](https://www.djangoproject.com/)
[![Django Rest Framework](https://img.shields.io/badge/django_rest_framework-3.4.0-blue.svg?style=flat-square)](http://www.django-rest-framework.org/)
[![Build Status](https://travis-ci.org/Harry-zklcdc/OnlineJudge.svg?branch=master)](https://travis-ci.org/Harry-zklcdc/OnlineJudge)

> #### 基于 Python 和 Vue 的在线评测系统。 [Demo](https://oj.yangzheng.com.cn/)

[English Document](README.md)



## 概览

- 基于 Docker，真正一键部署
- 前后端分离，模块化编程，微服务
- ACM/OI 两种比赛模式、实时/非实时评判 任意选择
- 丰富的可视化图表，一图胜千言
- 支持 Template Problem，可以添加函数题甚至填空题
- 更细致的权限划分，超级管理员和普通管理员各司其职
- 多语言支持：`C`, `C++`, `Java`, `Python2`, `Python3`，题目可以选择使用的语言
- Markdown & MathJax 支持
- 比赛用户IP限制 (CIDR ranges)
- 在线 IDE
- 自定义关于我们介绍页面
- 换肤功能
- 签到系统
- 经验系统
- 称号系统
- 标准输入输出 / 文件输入输出

主要模块均已开源:

- 后端(Django): [https://github.com/Harry-zklcdc/OnlineJudge](https://github.com/Harry-zklcdc/OnlineJudge)
- 前端(Vue): [https://github.com/Harry-zklcdc/OJ](https://github.com/Harry-zklcdc/OJ)
- 判题沙箱(Seccomp): [https://github.com/Harry-zklcdc/Judger](https://github.com/Harry-zklcdc/Judger)
- 判题服务器(对Judger的封装): [https://github.com/Harry-zklcdc/JudgeServer](https://github.com/Harry-zklcdc/JudgeServe)

## 安装

请根据此进行安装:  [https://github.com/Harry-zklcdc/OnlineJudgeDeploy/tree/2.0](https://github.com/Harry-zklcdc/OnlineJudgeDeploy/tree/2.0)

## 文档

[https://docs.onlinejudge.me/](https://docs.onlinejudge.me/)

## 截图

### OJ前台

![home page](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/%E9%A6%96%E9%A1%B5.jpg)

![announcement](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/%E5%85%AC%E5%91%8A.jpg)

![problem-list](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/%E9%A2%98%E7%9B%AE-%E5%8E%9F%E8%B0%85%E7%BB%BF.jpg)

![problem-details](https://user-images.githubusercontent.com/20637881/33372507-4061a782-d539-11e7-8835-076ddae6b529.png)

![statistic-info](https://user-images.githubusercontent.com/20637881/33372508-40a0c6ce-d539-11e7-8d5e-024541b76750.png)

![online-IDE](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/%E5%9C%A8%E7%BA%BFIDE.jpg)

![FAQ](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98-%E5%B0%91%E5%A5%B3%E7%B2%89.jpg)

![contest-list](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/%E6%AF%94%E8%B5%9B-%E5%9F%BA%E4%BD%AC%E7%B4%AB.jpg)

Rankings 中可以控制图表和菜单的显隐。

![acm-rankings](https://user-images.githubusercontent.com/20637881/33372510-41117f68-d539-11e7-9947-70e60bad3cf2.png)

![oi-rankings](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/%E6%8E%92%E5%90%8D.jpg)

![status](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/状态.jpg)

![status-details](https://user-images.githubusercontent.com/20637881/33365523-787bd0ea-d523-11e7-953f-dacbf7a506df.png)

![user-home](https://raw.githubusercontent.com/Harry-zklcdc/docs/master/image/个人中心.jpg)

### 后台管理

![admin-users](https://user-images.githubusercontent.com/20637881/33372516-42c34fda-d539-11e7-9f4e-5109477f83be.png)

![judge-server](https://user-images.githubusercontent.com/20637881/33372517-42faef9e-d539-11e7-9f17-df9be3583900.png)

![create-problem](https://user-images.githubusercontent.com/20637881/33372513-42472162-d539-11e7-8659-5497bf52dbea.png)

![create-contest](https://user-images.githubusercontent.com/20637881/33372514-428ab922-d539-11e7-8f68-da55dedf3ad3.png)

## 浏览器支持

Modern browsers(chrome, firefox) 和 Internet Explorer 10+.

## 特别感谢

- 所有为本项目做出贡献的人
- [heb1c](https://github.com/hebicheng) 同学为我们提供了很多意见和建议

如果您觉得这个项目还不错，就star一下吧 ：)

## 许可

The [MIT](http://opensource.org/licenses/MIT) License

