require(["jquery", "codeMirror", "csrfToken", "bsAlert", "ZeroClipboard"],
    function ($, codeMirror, csrfTokenHeader, bsAlert, ZeroClipboard) {
        // 复制样例需要 Flash 的支持 检测浏览器是否安装了 Flash
        function detect_flash() {
            var ie_flash;
            try {
                ie_flash = (window.ActiveXObject && (new ActiveXObject("ShockwaveFlash.ShockwaveFlash")) !== false)
            } catch (err) {
                ie_flash = false;
            }
            var _flash_installed = ((typeof navigator.plugins != "undefined" && typeof navigator.plugins["Shockwave Flash"] == "object") || ie_flash);
            return _flash_installed;
        }

        if(detect_flash()) {
            // 提供点击复制到剪切板的功能
            ZeroClipboard.config({swfPath: "/static/img/ZeroClipboard.swf"});
            new ZeroClipboard($(".copy-sample"));
        }
        else{
            $(".copy-sample").hide();
        }

        var codeEditorSelector = $("#code-editor")[0];
        // 部分界面逻辑会隐藏代码输入框，先判断有没有。
        if (codeEditorSelector == undefined) {
            return;
        }

        function getLanguage(){
            return $("input[name='language'][checked]").val();
        }

        var codeEditor = codeMirror(codeEditorSelector, "text/x-csrc");
        var language = getLanguage();
        var submissionId;
        var userId;

        function setLanguage(language){
            var languageTypes = {"1": "text/x-csrc", "2": "text/x-c++src", "3": "text/x-java"};
            codeEditor.setOption("mode", languageTypes[language]);
        }

        function saveCode(code){
            localStorage.setItem(userId + ":" + location.href, JSON.stringify({code: code, language: language}))
        }

        $("input[name='language']").change(function () {
            language = this.value;
            setLanguage(language);
        });

        $("#show-more-btn").click(function () {
            $(".hide").attr("class", "problem-section");
            $("#show-more-btn").hide();
        });

        function showLoading() {
            $("#submit-code-button").attr("disabled", "disabled");
            $("#loading-gif").show();
        }

        function hideLoading() {
            $("#submit-code-button").removeAttr("disabled");
            $("#loading-gif").hide();
        }

        function getResultHtml(data) {
            // 0 结果正确 1 运行错误 2 超时 3 超内存 4 编译错误
            // 5 格式错误 6 结果错误 7 系统错误 8 等待判题
            var results = {
                0: {"alert_class": "success", message: "Accepted"},
                1: {"alert_class": "danger", message: "Runtime Error"},
                2: {"alert_class": "warning", message: "Time Limit Exceeded"},
                3: {"alert_class": "warning", message: "Memory Limit Exceeded"},
                4: {"alert_class": "danger", message: "Compile Error"},
                5: {"alert_class": "warning", message: "Format Error"},
                6: {"alert_class": "danger", message: "Wrong Answer"},
                7: {"alert_class": "danger", message: "System Error"},
                8: {"alert_class": "info", message: "Waiting"}
            };

            var html = '<div class="alert alert-' +
                results[data.result].alert_class + ' result"' +
                ' role="alert">' +
                '<div class="alert-link">' +
                results[data.result].message +
                '!&nbsp;&nbsp; ';
            if (!data.result) {
                html += "CPU time: " + data.accepted_answer_time + "ms &nbsp;&nbsp;";
            }
            html += ('<a href="/submission/' + submissionId + '/" target="_blank">查看详情</a></div> </div>');

            return html;
        }

        var counter = 0;

        function getResult() {
            if (counter++ > 10) {
                hideLoading();
                bsAlert("抱歉，服务器正在紧张判题中，请稍后到我的提交列表中查看");
                counter = 0;
                return;
            }
            $.ajax({
                url: "/api/submission/?submission_id=" + submissionId,
                method: "get",
                dataType: "json",
                success: function (data) {
                    if (!data.code) {
                        // 8是还没有完成判题
                        if (data.data.result == 8) {
                            // 1秒之后重新去获取
                            setTimeout(getResult, 1000);
                        }
                        else {
                            counter = 0;
                            hideLoading();
                            $("#result").html(getResultHtml(data.data));
                        }
                    }
                    else {
                        bsAlert(data.data);
                        hideLoading();
                    }
                },
                error: function(){
                    bsAlert("额 好像出错了，请刷新页面重试。")
                }
            })
        }

        function guessLanguage(code) {
            //cpp
            if (code.indexOf("using namespace std") > -1||code.indexOf("<cstdio>") > -1) {
                return "2";
            }
            if (code.indexOf("printf") > -1||code.indexOf("<stdio.h>") > -1)
            {
                return "1";
            }
            //java
            if (code.indexOf("public class Main") > -1||code.indexOf("System.out.print") > -1) {
                return "3";
            }
        }

        function getServerTime(){
            var contestId = location.pathname.split("/")[2];
            var time = 0;
            $.ajax({
                url: "/api/contest/time/?contest_id=" + contestId + "&type=end",
                dataType: "json",
                method: "get",
                async: false,
                success: function(data){
                    if(!data.code){
                        time = data.data;
                    }
                }
            });
            return time;
        }

        if(location.href.indexOf("contest") > -1) {
            setInterval(function () {
                var time = getServerTime();
                if(time["status"] == 0){
                    var minutes = parseInt(time["end"] / (1000 * 60));
                    if(minutes == 0){
                        bsAlert("比赛即将结束");
                    }
                    else if(minutes > 0 && minutes <= 5){
                        bsAlert("比赛还剩" + minutes.toString() + "分钟");
                    }
                }

            }, 1000 * 60);
        }

        $("#submit-code-button").click(function () {

            var code = codeEditor.getValue();

            if (!code.trim()) {
                bsAlert("请填写代码！");
                hideLoading();
                return false;
            }

            if (guessLanguage(code) != language) {
                if (!confirm("您选择的代码语言可能存在错误，是否继续提交？")) {
                    return;
                }
            }

            if (language < 3) {
                if (code.indexOf("__int64") > -1) {
                    if (!confirm("您是否在尝试使用'__int64'类型? 这不是 C/C++ 标准并将引发编译错误，可以使用'long long'代替，详见帮助。是否继续提交？")) {
                        return;
                    }
                }
                if (code.indexOf("%I64d") > -1) {
                    if (!confirm("您是否在尝试将'%I64d'用于long long类型的IO? 这不被支持，并可能会导致程序输出异常，可以使用'%lld'代替，详见帮助。是否继续提交？")) {
                        return;
                    }
                }
            }
       
            if (location.href.indexOf("contest") > -1) {
                var problemId = location.pathname.split("/")[4];
                var contestId = location.pathname.split("/")[2];
                var url = "/api/contest/submission/";
                var data = {
                    problem_id: problemId,
                    language: language,
                    code: code,
                    contest_id: contestId
                };
            }
            else {
                var problemId = window.location.pathname.split("/")[2];
                var url = "/api/submission/";
                var data = {
                    problem_id: problemId,
                    language: language,
                    code: code
                };
            }

            showLoading();

            $("#result").html("");

            $.ajax({
                beforeSend: csrfTokenHeader,
                url: url,
                method: "post",
                data: JSON.stringify(data),
                contentType: "application/json;charset=UTF-8",
                success: function (data) {
                    if (!data.code) {
                        submissionId = data.data.submission_id;
                        // 获取到id 之后2秒去查询一下判题结果
                        setTimeout(getResult, 2000);
                    }
                    else {
                        bsAlert(data.data);
                        hideLoading();
                    }
                }
            });

        });

        $.ajax({
            url: "/api/user/",
            method: "get",
            dataType: "json",
            success: function (data) {
                if (data.code) {
                    $("#submit-code-button").attr("disabled", "disabled");
                    $("#result").html('<div class="alert alert-danger" role="alert">' +
                        '<div class="alert-link">请先' +
                        '<a href="/login/?__from=' + location.pathname + '" target="_blank">' +
                        '登录</a>!</div> </div>');
                }
                else{
                    userId = data.data.id;
                    if(window.localStorage){
                        var data = localStorage[userId + ":" + location.href];
                        if(data){
                            data = JSON.parse(data);
                            $("input[name='language'][value='" + data.language + "']").prop("checked", true);
                            language = data.language;
                            codeEditor.setValue(data.code);
                            setLanguage(data.language);
                        }

                        setInterval(function(){
                            saveCode(codeEditor.getValue())
                        }, 3000);
                    }
                }
            }
        })
    });