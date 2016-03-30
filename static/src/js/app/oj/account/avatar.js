require(["jquery", "bsAlert", "csrfToken"], function ($, bsAlert, csrfTokenHeader) {
    var avatar = "";

    function changeAvatar(event) {
        avatar = $(event.target).attr('src');
        $('#current_avatar').attr('src', avatar);
    }

    $('.avatar-item').click(changeAvatar);

    $('#save_avatar').click(function () {
        if (avatar)
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/account/userprofile/",
                data: {
                    avatar: avatar
                },
                dataType: "json",
                method: "put",
                success: function (data) {
                    if (!data.code) {
                        bsAlert("已保存!");
                    }
                    else {
                        bsAlert(data.data);
                    }
                },
                error: function () {
                    bsAlert("额 好像出错了，请刷新页面重试。如还有问题，请填写页面导航栏上的反馈。")
                }

            });
        else
            bsAlert("请选择一个头像");

    });
});

