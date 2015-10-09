require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    var applied_captcha = false;
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var username = $("#username").val();
            var password = $("#password").val();
            var captcha = $("#captcha").val();

            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/login/",
                data: {username: username, password: password, captcha: captcha},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if (!data.code) {
                        //成功登陆
                        var ref = document.referrer;
                        if (ref) {
                            // 注册页和本页的来源的跳转回首页，防止死循环
                            if (ref.indexOf("register") > -1 || ref.indexOf("login") > -1) {
                                location.href = "/";
                                return;
                            }
                            // 判断来源，只有同域下才跳转
                            if (ref.split("/")[2].split(":")[0] == location.hostname) {
                                location.href = ref;
                                return;
                            }
                        }
                        location.href = "/";
                    }
                    else {
                        if(applied_captcha) {
                            refresh_captcha();
                        }
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