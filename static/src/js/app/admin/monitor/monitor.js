require(["jquery", "chart"], function ($, Chart) {
    var data2 = {
        labels: ["January", "February", "March", "April", "May", "June", "July",
            "January", "February", "March", "April", "January", "February", "March", "April"],
        datasets: [
            {
                label: "2222222",
                fillColor: "rgba(50,187,205,0.2)",
                strokeColor: "rgba(151,187,205,1)",
                pointColor: "rgba(151,187,205,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(151,187,205,1)",
                data: [3, 7, 8, 9, 1, 4, 10, 10, 9, 8, 7, 10, 10, 10, 10]
            }
        ]
    };
    new Chart($("#waiting-queue-chart").get(0).getContext("2d")).Line(data2);

    var data = {
        labels: ["January", "February", "March", "April", "May", "June", "July",
            "January", "February", "March", "April", "January", "February", "March", "April"],
        datasets: [
            {
                label: "11111111",
                fillColor: "rgba(255,255,255,0.2)",
                strokeColor: "rgba(250,68,68,1)",
                pointColor: "rgba(220,220,220,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(220,220,220,1)",
                data: [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
            },
            {
                label: "2222222",
                fillColor: "rgba(50,187,205,0.2)",
                strokeColor: "rgba(151,187,205,1)",
                pointColor: "rgba(151,187,205,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(151,187,205,1)",
                data: [3, 7, 8, 9, 1, 4, 10, 10, 9, 8, 7, 10, 10, 10, 10]
            }
        ]
    };
    Chart.defaults.global.responsive = true;
    new Chart($("#judge-instance-chart").get(0).getContext("2d")).Line(data);

    var data1 = {
        labels: ["January", "February", "March", "April", "May", "June", "July",
            "January", "February", "March", "April", "January", "February", "March", "April"],
        datasets: [
            {
                label: "2222222",
                fillColor: "rgba(50,187,205,0.2)",
                strokeColor: "rgba(151,187,205,1)",
                pointColor: "rgba(151,187,205,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(151,187,205,1)",
                data: [3, 7, 8, 9, 1, 4, 10, 10, 9, 8, 7, 10, 10, 10, 10]
            },
            {
                label: "2222222",
                fillColor: "rgba(50,187,205,0.2)",
                strokeColor: "rgba(252,214,48,1)",
                pointColor: "rgba(252,214,48,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(151,187,205,1)",
                data: [30, 70, 58, 49, 19, 44, 100, 100, 89, 88, 77, 50, 80, 66, 100]
            }
        ]
    };
    Chart.defaults.global.responsive = true;
    new Chart($("#c1").get(0).getContext("2d")).Line(data1);



});