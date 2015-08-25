require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {

    $('form').validator().on('submit', function (e) {
        e.preventDefault();
        var username = $("#username").val();
        var newPassword = $("#new_password ").val();
        var password = $("#password").val();
        $.ajax({
            beforeSend: csrfTokenHeader,
            url: "/api/change_password/",
            data: {username: username, new_password: newPassword, old_password: password},
            dataType: "json",
            method: "post",
            success: function (data) {
                if (!data.code) {
                    window.location.href = "/login/";
                }
                else {
                    bsAlert(data.data);
                }
            }
        });
        return false;
    });
});