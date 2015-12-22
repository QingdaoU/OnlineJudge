require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    var applied_captcha = false;
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var username = $("#username").val();
            var password = $("#password").val();
            var tfaCode = $("#tfa-code").val();
            console.log(tfaCode);
            if(tfaCode.length && tfaCode.length != 6){
                bsAlert("验证码为六位数字");
                return false;
            }

            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/login/",
                data: {username: username, password: password, tfa_code: tfaCode},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if (!data.code) {
                        if(data.data == "tfa_required"){
                            $("#tfa-area").show();
                            return false;
                        }
                        function getLocationVal(id){
                            var temp = unescape(location.search).split(id+"=")[1] || "";
                            return temp.indexOf("&")>=0 ? temp.split("&")[0] : temp;
                        }
                        var from = getLocationVal("__from");
                        if(from != ""){
                            window.location.href = from;
                        }
                        else{
                            location.href = "/";
                        }
                    }
                    else {
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

});