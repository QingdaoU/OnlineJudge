require(["jquery", "bs_alert", "csrf", "validation"], function($, bs_alert, csrfHeader){
    $("#change_password-form").formValidation({
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
                            message: "请填写旧密码"
                            }
                    }
                },
                new_password: {
                    validators: {
                        notEmpty: {
                            message: "请填写新密码"
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
                confirm_password: {
                    validators: {
                        notEmpty: {
                            message: "请填写确认密码"
                        },
                        confirm: {
                            original: $("#new_password"),
                            message: "两次输入的密码必须一致"
                        }
                    },
                }
            }
        }
    ).on('success.form.fv', function(e) {
            e.preventDefault();
            var username = $("#username").val();
            var new_password  = $("#new_password ").val();
            var password = $("#password").val();
            $.ajax({
                beforeSend: csrfHeader,
                url: "/api/change_password/",
                data: {username: username, new_password: new_password , old_password : password},
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