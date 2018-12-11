# OnlineJudge 2.0

定制版QDUOJ,添加了比赛rejudge,代码查重,用户名限制等功能,需要与[前端](https://github.com/ExpMango/OnlineJudgeFE)配合使用.

# Feature

## Contest rejudge功能:

管理员先将需要rejudge的题目隐藏起来，等若干秒使得队列里没有该题目的新提交，然后点击比赛中题目列表的rejudge按钮即可。（由于判提调度的问题偶尔会出现一血错误的情况，重新rejudge即可）

![rejudge界面][1]


## 用户名限制: 

在contest描述中 最后的地方添加 “limit:#xxxx#“(不包含引号)即可,其中xxxx为用户名需要满足的正则表达式，如 limit:#201[5-8]11[0-9]{4}# 将使得用户名为"2015111234"的用户能够进入比赛,而"acm201111"的用户不能进入比赛.

![限制描述示例][2]
![被限制示例][3]

## 比赛代码查重

比赛结束后在前台点击一键查重,然后进入查重页面即可看到结果(未完成)

# Todo

- [x] 完成contest的rejudge功能
- [x] 添加contest用户名限制功能(正则检查)
- [ ] 重写contest rank字段,更好的支持rejudge功能
- [ ] contest代码相似查重 (后台已完成,前台Todo)



## License

[MIT](http://opensource.org/licenses/MIT)


  [1]: https://raw.githubusercontent.com/HandsomeHow/OnlineJudge/master/docs/rejudge_in_contest.png
  [2]: https://raw.githubusercontent.com/HandsomeHow/OnlineJudge/master/docs/limit_example.png
  [3]: https://raw.githubusercontent.com/HandsomeHow/OnlineJudge/master/docs/limit_result.png
