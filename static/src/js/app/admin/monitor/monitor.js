require(["jquery", "chart"], function ($, Chart) {
    var data = {
        labels: ["初始化"],
        datasets: [
            {
                label: "队列长度",
                fillColor: "rgba(255,255,255,0.2)",
                strokeColor: "rgba(151,187,205,1)",
                pointColor: "rgba(151,187,205,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(151,187,205,1)",
                data: [0]
            }
        ]
    };
    var chart = new Chart($("#waiting-queue-chart").get(0).getContext("2d")).Line(data);

    var dataCounter = 0;

    function getMonitorData(){
        var hash = location.hash;
        if (hash != "#monitor/monitor"){
            clearInterval(intervalId);
        }
        $.ajax({
            url: "/api/admin/monitor/",
            method: "get",
            dataType: "json",
            success: function(data){
                if(!data.code){
                    chart.addData([data.data["count"]], data.data["time"])
                    dataCounter ++;
                }
            }
        })
    }

    $("#clear-chart-data").click(function(){
        for(var i = 0;i < dataCounter;i++) {
            chart.removeData();
            dataCounter = 0;
        }
    });

    var intervalId = setInterval(getMonitorData, 3000);

});