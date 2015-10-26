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
                        function getLocationVal(id){
                            var temp = unescape(location.search).split(id+"=")[1] || "";
                            return temp.indexOf("&")>=0 ? temp.split("&")[0] : temp;
                        }
                        var from = getLocationVal("__from");
                        if(from != ""){
                            console.log(from);
                            window.location.href = from;
                        }
                        else{
                            location.href = "/";
                        }
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