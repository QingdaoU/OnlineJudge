require(["jquery", "bs_alert", "csrf", "validation"], function($, bs_alert, csrfHeader){
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
                        usernameCheck:{
                            message: '用户名已存在'
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
                    onSuccess: function(e, data) {
                            data.fv.revalidateField('confirm_password');
                    }
                },
                real_name: {
                    validators: {
                        notEmpty: {
                            message: "请填写真实姓名"
                            }
                    },
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
                }
            }
        }
    ).on('success.form.fv', function(e) {
            e.preventDefault();
            var username = $("#username").val();
            var real_name = $("#real_name").val();
            var password = $("#password").val();
            $.ajax({
                beforeSend: csrfHeader,
                url: "/api/register/",
                data: {username: username, real_name: real_name, password: password},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if(!data.code){
                        window.location.href="/login/";
                    }
                    else{
                        bs_alert(data.data);
                    }
                }

            })
        });

});