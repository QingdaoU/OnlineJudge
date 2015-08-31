require(["jquery", "csrfToken", "bsAlert"], function ($, csrfTokenHeader, bsAlert) {
    $("#sendApplication").click(function (){
        var message = $("#applyMessage").val();
        console.log(message);
        var groupId = window.location.pathname.split("/")[2];
        console.log(groupId);
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
