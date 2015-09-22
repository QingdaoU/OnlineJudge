require(["jquery", "jcountdown"], function($, jcountdown){

    function getServerTime(){
        var contestId = location.pathname.split("/")[2];

        var time = 0;
        $.ajax({
            url: "/api/contest/time/?contest_id=" + contestId,
            dataType: "json",
            method: "get",
            async: false,
            success: function(data){
                if(!data.code){
                    time = data.data;
                }
            }
        });
        return time;
    }

    var time = getServerTime();

    if(time["status"] == 1){
        countdown(time["start"])
    }
    else if(time["status"] == 0){
        countdown(time["end"])
    }

    function countdown(t){
        $("#timer").countdown({
            serverDiff: t,
            date: "september 21, 2015 21:59",
            yearsAndMonths: false,
            template: $('#template').html()
        }).on("countComplete", function(){
            location.reload();
        });
    }
});