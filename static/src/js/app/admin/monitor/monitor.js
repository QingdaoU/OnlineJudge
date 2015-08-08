require(["jquery", "chart"], function ($, Chart) {
    var data = {
        labels: ["January", "February", "March", "April", "May", "June", "July",
            "January", "February", "March", "April", "January", "February", "March", "April"],
        datasets: [
            {
                label: "11111111",
                fillColor: "rgba(220,220,220,0.2)",
                strokeColor: "rgba(220,220,220,1)",
                pointColor: "rgba(220,220,220,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(220,220,220,1)",
                data: [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
            },
            {
                label: "2222222",
                fillColor: "rgba(151,187,205,0.2)",
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
    var myLineChart = new Chart($("#myChart").get(0).getContext("2d")).Line(data);

    var data1 = [
    {
        value: 300,
        color:"#F7464A",
        highlight: "#FF5A5E",
        label: "Red"
    },
    {
        value: 50,
        color: "#46BFBD",
        highlight: "#5AD3D1",
        label: "Green"
    },
    {
        value: 100,
        color: "#FDB45C",
        highlight: "#FFC870",
        label: "Yellow"
    }
];


    new Chart($("#c1").get(0).getContext("2d")).Pie(data1);
    new Chart($("#c2").get(0).getContext("2d")).Pie(data1);

});