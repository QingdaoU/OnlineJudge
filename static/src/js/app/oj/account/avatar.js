require(["jquery", "bsAlert", "csrfToken", "uploader"], function ($, bsAlert, csrfTokenHeader, uploader) {
    var avatar = "";
    var avatarUploader = uploader("#avatarUploader", "/api/avatar/upload/",
        {title: 'Images', extensions: 'gif,jpg,jpeg,bmp,png', mimeTypes: 'image/*'},
        function (file, response) {
            if (response.code) {
                bsAlert(response.data);
            }
            else {
                avatar = response.data.path;
                $('#current-avatar').attr('src', avatar);
            }
        });


    function changeAvatar(event) {
        avatar = $(event.target).attr('src');
        $('#current-avatar').attr('src', avatar);
    }

    $('.avatar-item').click(changeAvatar);

    $('#save-avatar').click(function () {
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

