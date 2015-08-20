require(["jquery", "chart"], function ($, Chart) {
    var data = {
        labels: ["初始化"],
        datasets: [
            {
                label: "2222222",
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

    function getMonitorData(){
        $.ajax({
            url: "/api/admin/monitor/",
            method: "get",
            dataType: "json",
            success: function(data){
                if(!data.code){
                    chart.addData([data.data["count"]], data.data["time"])
                }
            }
        })
    }

    $("#clear-chart-data").click(function(){
        chart.removeData();
    });

    setInterval(getMonitorData, 3000);

});