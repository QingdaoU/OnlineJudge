require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var username = $("#username").val();
            var realName = $("#real_name").val();
            var password = $("#password").val();
            var email = $("#email").val();
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/register/",
                data: {username: username, real_name: realName, password: password, email: email},
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
        }
    })
});