require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {

    function refresh_captcha(){
        $("#captcha-img")[0].src = "/captcha/?" + Math.random();
        $("#captcha")[0].value = "";
    }
    $("#captcha-img").click(function(){
        refresh_captcha();
    });

    $('form').validator().on('submit', function (e) {
        e.preventDefault();
        var newPassword = $("#new_password ").val();
        var password = $("#password").val();
        var captcha = $("#captcha").val();
        $.ajax({
            beforeSend: csrfTokenHeader,
            url: "/api/change_password/",
            data: {new_password: newPassword, old_password: password, captcha: captcha},
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
            }
        });
        return false;
    });
});