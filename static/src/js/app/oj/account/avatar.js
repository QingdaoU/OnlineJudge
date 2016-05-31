require(["jquery", "bsAlert", "csrfToken", "uploader"], function ($, bsAlert, csrfTokenHeader, uploader) {
    var avatar = "";
    var avatarUploader = uploader("#avatarUploader", "/",
        {title: 'Images', extensions: 'gif,jpg,jpeg,bmp,png', mimeTypes: 'image/*'},
        function (file, response) {
            //todo
        });


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
                    bsAlert("好像出错了，请刷新页面重试。")
                }

            });
        else
            bsAlert("请选择一个头像");

    });
});

