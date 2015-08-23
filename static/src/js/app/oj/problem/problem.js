require(["jquery", "codeMirror", "csrfToken", "bsAlert"], function ($, codeMirror, csrfTokenHeader, bsAlert) {
    var codeEditor = codeMirror($("#code-editor")[0], "text/x-csrc");
    var language = $("input[name='language'][checked]").val();
    var submissionId;

    $("input[name='language']").change(function () {
        language = this.value;
        var languageTypes = {"1": "text/x-csrc", "2": "text/x-c++src", "3": "text/x-java"};
        codeEditor.setOption("mode", languageTypes[language]);
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
        html += ('<a href="/my_submission/' + submissionId + '/" target="_blank">查看详情</a></div> </div>');

        return html;
    }

    var counter = 0;

    function getResult() {
        if(counter++ > 10){
            hideLoading();
            bsAlert("抱歉，服务器可能出现了故障，请稍后到我的提交列表中查看");
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
            }
        })
    }

    $("#submit-code-button").click(function () {
        var problemId = window.location.pathname.split("/")[2];
        var code = codeEditor.getValue();

        showLoading();

        if(!code.trim()){
            bsAlert("请填写代码！");
            hideLoading();
            return false;
        }

        $("#result").html("");

        $.ajax({
            beforeSend: csrfTokenHeader,
            url: "/api/submission/",
            method: "post",
            data: JSON.stringify({
                problem_id: problemId,
                language: language,
                code: codeEditor.getValue()
            }),
            contentType: "application/json",
            success: function (data) {
                if (!data.code) {
                    submissionId = data.data.submission_id;
                    // 获取到id 之后2秒去查询一下判题结果
                    setTimeout(getResult, 2000);
                }
                else {
                    bs_alert(data.data);
                    hideLoading();
                }
            }
        });

    });

    $.ajax({
        url : "/api/user/",
        method: "get",
        dataType: "json",
        success: function(data){
            if(data.code){
                $("#submit-code-button").attr("disabled", "disabled");
                $("#result").html('<div class="alert alert-danger" role="alert"><div class="alert-link">请先<a href="/login/" target="_blank">登录</a>!</div> </div>');
            }
        }
    })
});
