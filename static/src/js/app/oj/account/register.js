require(["jquery", "bs_alert", "csrf", "validation"], function ($, bs_alert, csrfHeader) {
    $("#register-form")
        .formValidation({
            framework: "bootstrap",
            fields: {
                username: {
                    validators: {
                        notEmpty: {
                            message: "请填写用户名"
                        },
                        stringLength: {
                            min: 3,
                            max: 30,
                            message: '用户名长度必须在3到30位之间'
                        },
                        remote: {
                            message: "用户名已存在",
                            url: "/api/username_check/",
                            field: 'username'
                        }
                    }
                },
                password: {
                    validators: {
                        notEmpty: {
                            message: "请填写密码"
                        },
                        stringLength: {
                            min: 6,
                            max: 30,
                            message: '密码长度必须在6到30位之间'
                        }
                    },
                    onSuccess: function (e, data) {
                        data.fv.revalidateField('confirm_password');
                    }
                },
                real_name: {
                    validators: {
                        notEmpty: {
                            message: "请填写真实姓名"
                        }
                    }
                },
                confirm_password: {
                    validators: {
                        notEmpty: {
                            message: "请填写确认密码"
                        },
                        confirm: {
                            original: $("#password"),
                            message: "两次输入的密码必须一致"
                        }
                    }
                },
                email: {
                    validators: {
                        notEmpty: {
                            message: "请填写电子邮箱邮箱地址"
                        },
                        emailAddress: {
                            message: "请填写有效的邮箱地址"
                        },
                        remote: {
                            message: "您已经注册过了",
                            url: "/api/email_check/",
                            field: 'email'
                        }
                    }
                }
            }
        }
    ).on('success.form.fv', function (e) {
            e.preventDefault();
            var username = $("#username").val();
            var real_name = $("#real_name").val();
            var password = $("#password").val();
            var email = $("#email").val();
            $.ajax({
                beforeSend: csrfHeader,
                url: "/api/register/",
                data: {username: username, real_name: real_name, password: password, email: email},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if (!data.code) {
                        window.location.href = "/login/";
                    }
                    else {
                        bs_alert(data.data);
                    }
                }
            })
        });
});