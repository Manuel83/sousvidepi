$(document).ready(function () {

    var settings = {
        series: {
            lines: {
                fill: false,
                lineWidth: 3

            },
            shadowSize: 0
        },
        colors: ["#8ecaff"],
        grid: {
            borderWidth: 0,

            show: true
        },
        xaxis: {
            show: true,
            tickColor: "#fff",
            color: "#fff",
            tickLength: 0,
            font: {
                color: "#fff"
            },
            mode: "time",
            timezone: "browser",
            ticks: 3
        },
        yaxis: {
            tickDecimals: 2,
            show: true,
            color: "#8ecaff",
            font: {
                color: "#fff"
            }
        }
    };
    var count = 0;

    var d1 = [];
    var plot = $.plot("#temp_chart", [d1], settings);
    var myVar = setInterval(function () {
        getTemp()
    }, 1000);


    console.log(new Date().getTime());

    function getTemp() {
        $.ajax({
            url: "getTemp",
            dataType: "json",
            context: document.body
        }).done(function (data) {
            // console.log(data);
            $("#tmpvalue").html(data.temp);
            $("#heat_value").html(data.heat);

            count++;
            d1.push([new Date().getTime(), data.temp]);
            plot.setData([d1]);
            plot.setupGrid();
            plot.draw();
            //$("#tmpvalue").html(data);
        });

    }

    $("#auto").click(function () {
        console.log("AUTO");

        $.ajax({
            url: "auto",
            context: document.body
        }).done(function () {
            console.log("DONE");
        });
    });

    $("#setdata").click(function () {
        console.log("AUTO");

        $.ajax({
            url: "setData",
            data: {

                tt: $("#tt").val(),
                kp: $("#kp").val(),
                ki: $("#ki").val(),
                kd: $("#kd").val()
            },
            context: document.body
        }).done(function () {
            console.log("DONE");
        });
    });








});