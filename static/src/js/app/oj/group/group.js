require(["jquery", "csrfToken", "bsAlert"], function ($, csrfTokenHeader, bsAlert) {
    $("#sendApplication").click(function (){
        var message;
        if ($("#applyMessage").length) {
            message = $("#applyMessage").val();
            if (!message)
                bsAlert("提交失败,请填写申请信息!");
                return false;
        }

        var groupId = window.location.pathname.split("/")[2];
        data = {group_id: groupId,message:message}
        $.ajax({
            url: "/api/group_join/",
            method: "post",
            dataType: "json",
            beforeSend: csrfTokenHeader,
            data: JSON.stringify(data),
            contentType: "application/json",
            success: function (data) {
                if (data.code) {
                    bsAlert(data.data);
                }
                else {
                    bsAlert("申请已提交!");
                }
            }
        })
    })
})
