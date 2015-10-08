require(["jquery", "bsAlert", "csrfToken"], function($, bsAlert, csrfTokenHeader){
   $("#contest-password-btn").click(function(){
       var password = $("#contest-password").val();
       if(!password){
           bsAlert("密码不能为空!");
           return;
       }
       $.ajax({
           beforeSend: csrfTokenHeader,
           url: "/api/contest/password/",
           data: {password: password, contest_id: location.href.split("/")[4]},
           method: "post",
           dataType: "json",
           success: function(data){
               if(!data.code){
                   location.reload();
               }
               else{
                   bsAlert(data.data);
               }
           },
            error: function(){
                bsAlert("额 好像出错了，请刷新页面重试。如还有问题，请填写页面导航栏上的反馈。")
            }
       })
   })
});