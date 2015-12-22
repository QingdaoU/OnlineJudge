require(["jquery", "bsAlert", "csrfToken"], function ($, bsAlert, csrfTokenHeader) {
    $("#tfa_submit").click(function(){
        var code = $("#tfa_code").val();
        if (code.length != 6){
            bsAlert("验证码是6位数字");
            return;
        }
        $.ajax({
            beforeSend: csrfTokenHeader,
            url: "/api/two_factor_auth/",
            data: {code: code},
            dataType: "json",
            method: "post",
            success: function(data){
                if(data.code){
                    bsAlert(data.data);
                }
                else{
                    bsAlert("两步验证开启成功");
                    location.reload();
                }
            }
        })

    })
});

