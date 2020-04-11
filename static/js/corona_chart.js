let CONFIRMED_IX = 0;
let DEATHS_IX = 1;
let RECOVERED_IX = 2;
let ACTIVE_IX = 3;
let LOGFIT_IX = 4;

function download_canvas() {
	let url = $("#chart")[0].toDataURL("image/png;base64");
	let filename = 'COVID19_Chart.png';

	$("#download-chart")[0].href = url;
	$("#download-chart")[0].setAttribute("download", filename);
	$("#download-chart")[0].click();
}

function init_chart() {
	init_CORONA_GLOBALS();
	reload_chart();
	CORONA_GLOBALS.reload_function = reload_chart;
}

function init_CORONA_GLOBALS() {
    let chart = CORONA_GLOBALS.chart;

    $("select[name=scale-type]").change(
        function() {
            if (this.value == 'logarithmic' || this.value == 'linear') {
                CORONA_GLOBALS.scale_type = this.value;
                chart.options.scales.yAxes[0].type = this.value;
                chart.update();
            }
        }
    );

    $("select[name=chart-type]").change(
        function() {
            CORONA_GLOBALS.chart_type = this.value;
            CORONA_GLOBALS.reload_function();
        }
    );

    $("input[name=display-confirmed]").change(
        function() {
            chart.data.datasets[CONFIRMED_IX].hidden = !this.checked;
            chart.update();
        }
    );

    $("input[name=display-deaths]").change(
        function() {
            chart.data.datasets[DEATHS_IX].hidden = !this.checked;
            chart.update();
        }
    );

    $("input[name=display-recovered]").change(
        function() {
            chart.data.datasets[RECOVERED_IX].hidden = !this.checked;
            chart.update();
        }
    );

    $("input[name=display-active]").change(
        function() {
            chart.data.datasets[ACTIVE_IX].hidden = !this.checked;
            chart.update();
        }
	);
	
	$("input#smoothing").change(
		function() {
			CORONA_GLOBALS.smoothing = this.value;
			reload_chart();
		}
	);

	$("input[name=display-logfit]").change(
		function() {
			chart.data.datasets[LOGFIT_IX].hidden = !this.checked;
			chart.update();
		}
	);
}

function new_chart(canvas_id) {
	let data = {
		labels: [],
		datasets: [
			{
				label: 'Confirmed cases',
				backgroundColor: 'yellow',
				borderColor: 'yellow',
				fill: false,
				data: [],
				lineTension: 0
			},
			{
				label: 'Deaths',
				backgroundColor: 'red',
				borderColor: 'red',
				fill: false,
				data: [],
				lineTension: 0
			},
			{
				label: 'Recovered',
				backgroundColor: 'green',
				borderColor: 'green',
				fill: false,
				data: [],
				lineTension: 0
			},
			{
				label: 'Active',
				backgroundColor: 'orange',
				borderColor: 'orange',
				fill: false,
				data: [],
				lineTension: 0,
				hidden: true
			},
			{
				label: 'Predicted cases',
				backgroundColor: 'grey',
				borderColor: 'grey',
				fill: false,
				data: [],
				lineTension: 0,
				hidden: false
			}
		]
	};
	return new Chart(get_canvas(canvas_id), {
		type: 'line',
		data: data,
		options: {
			responsive: true,
			title: {
				display: true,
				text: "Cases",
				fontColor: "#f5f5f5",
				fontSize: 30,
				fontStyle: "",
				fontFamily: "Lato"
			},
			legend: {
				display: true,
				labels: {
					fontColor: "#f5f5f5"
				}
			},
			hover: {
				mode: 'nearest',
				intersect: true
			},
			scales: {
				xAxes: [
					{
						gridLines: {
							color: "#f5f5f5"
						},
						ticks: {
							fontColor: "#f5f5f5"
						}
					}
				],
				yAxes: [
					{
						gridLines: {
							color: "#f5f5f5"
						},
						ticks: {
							fontColor: "#f5f5f5"
						}
					}
				]
			}
		}
	});
}

function get_canvas(a) {
	return document.getElementById(a).getContext('2d');
}

function reset_chart() {
	let chart = CORONA_GLOBALS.chart;
	chart.options.title.text = 'Cases';
	chart.data.labels = [];
	for (let i = 0; i < chart.data.datasets.length; i++) {
		chart.data.datasets[i].data = [];
	}
	chart.update();
}

function add_chart_data(data) {
	reset_chart();
	let chart = CORONA_GLOBALS.chart;
	let raw = [[], [], [], [], []];

	chart.data.labels = data.entry_date;
	let datasets = chart.data.datasets;
	let extend_dates = data.entry_date.length;


	if (CORONA_GLOBALS.chart_type == 'total') {
		raw[CONFIRMED_IX] = data.confirmed;
		raw[DEATHS_IX] = data.deaths;
		raw[RECOVERED_IX] = data.recovered;
		raw[ACTIVE_IX] = data.active;

		raw[LOGFIT_IX] = generate_fit_data(data.fit, start=0, end=data.entry_date.length + extend_dates);
		chart.data.labels = generate_dates(new Date(data.entry_date[0]), data.entry_date.length + extend_dates);
	} else if (CORONA_GLOBALS.chart_type == 'daily-change') {
		raw[CONFIRMED_IX] = data.dconfirmed;
		raw[DEATHS_IX] = data.ddeaths;
		raw[RECOVERED_IX] = data.drecovered;
		raw[ACTIVE_IX] = data.dactive;

		raw[LOGFIT_IX] = generate_derivative_data(data.fit, start=0, end=data.entry_date.length + extend_dates);
		chart.data.labels =  generate_dates(new Date(data.entry_date[0]), data.entry_date.length + extend_dates);
	}

	// NUMBER OF SLOTS FOR DATA
	for (let i = 0; i < 5; i++) {
		datasets[i].data = smooth_data(raw[i], CORONA_GLOBALS.smoothing);
	}

	chart.update()
}

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

function generate_fit_data(fit, start=0, end=10) {
	let data = [];
	for (let i = start; i < end; i++) {
		data.push(predict(fit, i));
	}
	return data;
}

function predict(fit, x) {
	return fit.c/(1 + fit.a * Math.exp(-x * fit.b));
}

function smooth_data(array, smoothing) {
	// smoothing is too high
	if (smoothing > array.length - 1) {
		smoothing = array.length - 1;
	}

	// now, we use a map function
	let smooth_array = array.map((value, index) => {
		// at a certain index, take the values N days before and N days after
		let taken_left = Math.min(smoothing, index);
		let taken_right = Math.min(smoothing, (array.length - 1 - index));
		let values = array.slice(index - taken_left, index + taken_right + 1);
		let sum = values.reduce((a, b) => (a + b));

		let missing_right = (smoothing - taken_right);
		let missing_left = (smoothing - taken_left);

		sum += missing_right * array[array.length - 1];
		sum += missing_left * array[0];

		return sum / (2 * smoothing + 1);
	});

	return smooth_array;
}

function reload_chart() {
	reset_chart();
	
	let country = CORONA_GLOBALS.country;
	let province = CORONA_GLOBALS.province;
	let admin2 = CORONA_GLOBALS.admin2;
	
	let label = generate_name(country, province, admin2);

	let chart = CORONA_GLOBALS.chart;

	let params = {
		country: country,
		province: province,
		admin2: admin2,
		world: "World"
	}
	
	$.getJSON(
		"/cases/totals_sequence",
		params,
		function(data) {
			add_chart_data(data);
			chart.options.title.text = 'Cases in: ' + label;
			chart.update();
		}
	)
}