require(["jquery", "bsAlert", "csrfToken", "validator"], function ($, bsAlert, csrfTokenHeader) {
    $('form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var phone = $("#phone").val();
            var hduoj_username = $("#hduoj_username").val();
            var bestcoder_username = $("#bestcoder_username").val();
            var codeforces_username = $("#codeforces_username").val();
            var blog = $("#blog").val();
            var mood = $("#mood").val();
            var school = $("#school").val();
            var student_id = $("#student_id").val();
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/account/userprofile/",
                data: {
                    phone_number: phone,
                    hduoj_username: hduoj_username,
                    bestcoder_username: bestcoder_username,
                    codeforces_username: codeforces_username,
                    blog: blog,
                    mood: mood,
                    school: school,
                    student_id: student_id
                },
                dataType: "json",
                method: "put",
                success: function (data) {
                    if (!data.code) {
                        bsAlert("修改成功");
                    }
                    else{
                        bsAlert(data.data);
                    }
                },
                error: function () {
                    bsAlert("额 好像出错了，请刷新页面重试。如还有问题，请填写页面导航栏上的反馈。")
                }

            });
            return false;
        }
    });
});

