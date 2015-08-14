require(["jquery", "code_mirror", "csrf", "bs_alert"], function ($, code_mirror, csrfHeader, bs_alert) {
    var code_editor = code_mirror($("#code-editor")[0], "text/x-csrc");
    var language = $("input[name='language'][checked]").val();
    var submission_id;

    $("input[name='language']").change(function () {
        language = this.value;
        var language_types = {"1": "text/x-csrc", "2": "text/x-c++src", "3": "text/x-java"};
        code_editor.setOption("mode", language_types[language]);
    });

    $("#show-more-btn").click(function () {
        $(".hide").attr("class", "problem-section");
        $("#show-more-btn").hide();
    });

    function show_loading() {
        $("#submit-code-button").attr("disabled", "disabled");
        $("#loading-gif").show();
    }

    function hide_loading() {
        $("#submit-code-button").removeAttr("disabled");
        $("#loading-gif").hide();
    }


    function get_result_html(data) {
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
            html += "CPU time: " + data.accepted_answer_info.time + "ms &nbsp;&nbsp;";
        }
        html += ('<a href="/my_submission/' + submission_id + '/" target="_blank">查看详情</a></div> </div>');

        return html;
    }

    function get_result() {
        $.ajax({
            url: "/api/submission/?submission_id=" + submission_id,
            method: "get",
            dataType: "json",
            success: function (data) {
                if (!data.code) {
                    // 8是还没有完成判题
                    if (data.data.result == 8) {
                        // 1秒之后重新去获取
                        setTimeout(get_result, 1000);
                    }
                    else {
                        hide_loading();
                        $("#result").html(get_result_html(data.data));
                    }
                }
                else {
                    bs_alert(data.data);
                    hide_loading();
                }
            }
        })
    }

    $("#submit-code-button").click(function () {
        var problem_id = window.location.pathname.split("/")[2];
        var code = code_editor.getValue();

        show_loading();

        if(!code.trim()){
            bs_alert("请填写代码！");
            hide_loading();
            return false;
        }

        $("#result").html("");

        $.ajax({
            beforeSend: csrfHeader,
            url: "/api/submission/",
            method: "post",
            data: JSON.stringify({
                problem_id: window.location.pathname.split("/")[2],
                language: language,
                code: code_editor.getValue()
            }),
            contentType: "application/json",
            success: function (data) {
                if (!data.code) {
                    submission_id = data.data.submission_id;
                    // 获取到id 之后2秒去查询一下判题结果
                    setTimeout(get_result, 2000);
                }
                else {
                    bs_alert(data.data);
                    hide_loading();
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
