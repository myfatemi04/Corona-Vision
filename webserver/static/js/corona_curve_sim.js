let rate = 1;
let contact = 1;
let max_size = 320000000;
let max_hospital = 924000;
let chart = null;

function generate_dates(start_date, length) {
	let dates = [];
	let next_date = start_date;
	for (let i = 0; i < length; i++) {
		dates.push(next_date.toISOString().substring(0, 10));
		next_date.setDate(next_date.getDate() + 1);
	}
	return dates;
}

function generate_derivative_data(fit, start=0, end=10) {
	let data = [];
	let d = 0.001;
	for (let i = start; i < end; i++) {
		let diff = predict(fit, i + d) - predict(fit, i);
		let deriv = diff/d;
		data.push(deriv);
	}
	return data;
}

function generate_fit_data(start_value=0.01) {
    let data = [];
    // next day = today + today * (1 - (today)/(total))
    let today = start_value;

    if (rate == 0) {
        return [0, 0, 0, 0, 0, 0, 0];
    }

    let true_max = 0.3 * max_size;

    while (data.length < 400) {
        let next_day = today + contact * rate * today * (1 - today/(true_max));
        data.push(next_day - today);
        today = next_day;
    }
	
	return data;
}

function predict(fit, x) {
	return fit.c/(1 + fit.a * Math.exp(-fit.b * x));
}

function fill(value, len) {
    let data = [];
    for (let i = 0; i < len; i++) {
        data.push(value);
    }
    return data;
}

function reload_chart() {//https://data.worldbank.org/indicator/sh.med.beds.zs
    chart.data.datasets[0].data = generate_fit_data(start_value=max_size/500);
    chart.data.datasets[1].data = fill(max_hospital, len=400);//chart.data.datasets[0].data.length);
    chart.data.labels = [...Array(400).keys()];
    chart.options.scales.yAxes[0].ticks.max = max_size / 200 + Math.max(max_size / 200, max_hospital, Math.max(...chart.data.datasets[0].data));
    chart.update();
}

function init_curve_sim() {
    let canvas = $("#chart")[0].getContext('2d');
    let data = {
        labels: [],
        datasets: [
            {
                label: "Prediction",
                data: [],
                lineTension: 0,
                fill: false,
                backgroundColor: COLORS.fg,
                borderColor: COLORS.fg
            },
            {
                label: "Healthcare Capacity",
                date: [],
                lineTension: 0,
                fill: false,
                backgroundColor: "lightcoral",
                borderColor: "lightcoral"
            }
        ]
    };

    chart = new Chart(canvas, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            title: {
                display: true,
                text: "Curve simulator",
				fontColor: COLORS.fg,
				fontSize: 30,
				fontStyle: "",
				fontFamily: "Lato"
            },
			scales: {
				xAxes: [
					{
                        gridLines: {
                            color: COLORS.fg
						},
						ticks: {
                            fontColor: COLORS.fg,
                            min: 0,
                            max: 400
                        },
                        scaleLabel: {
                            display: true,
                            labelString: "Number of days",
                            fontColor: COLORS.fg
                        }
					}
				],
				yAxes: [
					{
                        gridLines: {
                            color: COLORS.fg
						},
						ticks: {
                            fontColor: COLORS.fg,
                            max: max_size,
                            min: 0
						},
                        scaleLabel: {
                            display: true,
                            labelString: "Number of people",
                            fontColor: COLORS.fg
                        }
					}
				]
			}
        }
    });

    $("#rate").change(
        function() {
            rate = this.value;
            reload_chart();
        }
    );

    $("#max_size").change(
        function() {
            max_size = parseInt($("#max_size option:selected").attr("data-pop"));
            max_hospital = parseInt($("#max_size option:selected").attr("data-health"));
            reload_chart();
        }
    );

    $("#contact").change(
        function() {
            contact = parseFloat($("#contact")[0].value);
            reload_chart();
        }
    );

    max_size = parseInt($("#max_size option:selected").attr("data-pop"));
    max_hospital = parseInt($("#max_size option:selected").attr("data-health"));
    rate = parseFloat($("#rate")[0].value);
    contact = parseFloat($("#contact")[0].value);

    reload_chart();
}