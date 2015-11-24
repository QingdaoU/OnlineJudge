require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var username = $("#username").val();
            var realName = $("#real_name").val();
            var school = $('#school').val();
            var password = $("#password").val();
            var email = $("#email").val();
            var captcha = $("#captcha").val();
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/register/",
                data: {username: username, school: school, real_name: realName, password: password, email: email, captcha:captcha},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if (!data.code) {
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
    function refresh_captcha() {
        $("#captcha-img")[0].src = "/captcha/?" + Math.random();
        $("#captcha")[0].value = "";
    }

    $("#captcha-img").click(function () {
        refresh_captcha();
    });
});