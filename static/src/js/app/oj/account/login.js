require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    var applied_captcha = false;
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var username = $("#username").val();
            var password = $("#password").val();
            var ajaxData = {username: username, password: password};
            if (applied_captcha) {
                ajaxData.captcha = $("#captcha").val();
            }
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/login/",
                data: ajaxData,
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
                        refresh_captcha();
                        bsAlert(data.data);
                    }
                }

            });
            return false;
        }
    });

    $('#username').blur(function () {
        if ($("#username").val()) {
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/account_security_check/?username=" + $("#username").val(),
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        if (data.data.applied_captcha) {
                            $('#captcha-area').html('<label for="captcha">验证码</label>&nbsp;&nbsp;<img src="/captcha/" id="captcha-img"><small><p></p></small><input type="text" class="form-control input-lg" id="captcha" name="captcha" placeholder="验证码" maxlength="4" data-error="请填写验证码" required><div class="help-block with-errors"></div>');
                            applied_captcha = true;
                        }
                        else {
                            $('#captcha-area').html('');
                            applied_captcha = false;
                        }
                    }
                }
            });
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