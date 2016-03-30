require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    var applied_captcha = false;
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var splited_location = location.href.split("/");
            var token = splited_location[splited_location.length-2];
            var captcha = $("#captcha").val();
            var password = $("#new_password").val();
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/reset_password/",
                data: {password: password, captcha: captcha, token:token},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if (!data.code) {
                        refresh_captcha();
                        bsAlert(data.data);
                        window.location.href = "/login/";
                    }
                    else {
                        refresh_captcha();
                        bsAlert(data.data);
                    }
                },
                error: function(){
                    bsAlert("额 好像出错了，请刷新页面重试。如还有问题，请填写页面导航栏上的反馈。")
                }

            });
            return false;
        }
    });
    function refresh_captcha(){
        $("#captcha-img")[0].src = "/captcha/?" + Math.random();
        $("#captcha")[0].value = "";
    }
    $("#captcha-img").click(function(){
        refresh_captcha();
    });
});