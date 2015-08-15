require(["jquery", "bsAlert", "csrfToken", "formValidation"], function ($, bsAlert, csrfTokenHeader) {
    $("#login-form")
        .formValidation({
            framework: "bootstrap",
            fields: {
                username: {
                    validators: {
                        notEmpty: {
                            message: "请填写用户名"
                        }
                    }
                },
                password: {
                    validators: {
                        notEmpty: {
                            message: "请填写密码"
                        }
                    }
                }
            }
        }
    ).on('success.form.fv', function (e) {
            e.preventDefault();
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
                        window.location.href = "/";
                    }
                    else {
                        bsAlert(data.data);
                    }
                }

            })
        });
});