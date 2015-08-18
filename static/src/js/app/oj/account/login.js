require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var username = $("#username").val();
            var password = $("#password").val();
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/login/",
                data: {username: username, password: password},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if (!data.code) {
                        //成功登陆
                        var ref = document.referrer;
                        if(ref){
                            if(ref.split("/")[2] == location.hostname){
                                location.href = ref;
                            }
                        }
                        location.href = "/";
                    }
                    else {
                        bsAlert(data.data);
                    }
                }

            });
            return false;
        }
    })
});