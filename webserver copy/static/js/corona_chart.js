let index = {
	total: 0,
	deaths: 1,
	recovered: 2,
	predicted: 3
};

let chart = null;
let chart_smoothing = 0;

let chart_type = "total";

let predictor_type = "none";
let log_predictor = {};
// let lstm_predictor = {};

let plugins = [{
	beforeDraw: function (chart, easing) {
		var ctx = chart.chart.ctx;

		ctx.save();
		ctx.fillStyle = "#212121";
		ctx.fillRect(0, 0, $("canvas")[0].width, $("canvas")[0].height);
		ctx.restore();
	}
}];

let waiting = null;

function download_canvas() {
	let url = $("#chart")[0].toDataURL("image/png;base64");
	let filename = 'COVID19_Chart.png';

	$("#download-chart")[0].href = url;
	$("#download-chart")[0].setAttribute("download", filename);
	$("#download-chart")[0].click();
}

function init_chart() {
	init_chart_options();
	reload_chart();
}

function init_chart_options() {
    $("select[name=scale-type]").change(
        function() {
            if (this.value == 'logarithmic' || this.value == 'linear') {
                chart.options.scales.yAxes[0].type = this.value;
                chart.update();
            }
        }
    );

    $("select[name=chart-type]").change(
        function() {
            chart_type = this.value;
            reload_chart();
        }
    );
	
	$("select[name=show_predictions]").change(
		function() {
			if (this.value == "log") {
				chart.data.datasets[index.predicted].data = [];
				predictor_type = "log";
				redraw_chart();
			} else if (this.value == "lstm") {
				chart.data.datasets[index.predicted].data = [];
				predictor_type = "lstm";
				redraw_chart();
			} else {
				predictor_type = "none";
				reset_predicted_data_datapoints();
				redraw_chart();
			}
		}	
	);
	
	$("input#smoothing").change(
		function() {
			chart_smoothing = this.value;
			reload_chart();
		}
	);
}

function new_chart(canvas_id) {
	let data = {
		labels: [],
		datasets: [
			{
				label: 'Total cases',
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
				label: 'Predicted Cases',
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
		plugins: plugins,
		options: {
			responsive: true,
			title: {
				display: true,
				text: "Loading",
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
	chart.options.title.text = 'Loading';
	chart.data.labels = [];
	for (let i = 0; i < chart.data.datasets.length; i++) {
		chart.data.datasets[i].data = [];
	}
	chart.update();
}

// ADD: total cases (predicted)
// ADD: mortality rate (predicted)
// ADD: time to recover (predicted)

function fix_data(data, extra_days) {
	// let last_date = new Date(data.entry_date[data.entry_date.length - 1]);
	// let first_date = new Date(data.entry_date[0]);
	// let diff = (last_date.getTime() - first_date.getTime());
	// let day_length = 1000 * 60 * 60 * 24;
	// let num_days = diff / day_length + 1;
	// let paired = {};
	// for (let i = 0; i < data.entry_date.length; i++) {
	// 	paired[data.entry_date[i]] = {
	// 		total: data.total[i],
	// 		recovered: data.recovered[i],
	// 		deaths: data.deaths[i],
	// 		dtotal: data.dtotal[i],
	// 		drecovered: data.drecovered[i],
	// 		ddeaths: data.ddeaths[i]
	// 	};
	// }

	// let new_days = null;

	// if (extra_days)
	// 	new_days = date_range(data.entry_date[0], num_days * 2);
	// else
	// 	new_days = date_range(data.entry_date[0], num_days);
	
	// let new_data = {};
	// let props = ['total', 'deaths', 'recovered', 'dtotal', 'ddeaths', 'drecovered'];
	// for (let day_n in new_days) {
	// 	let day = new_days[day_n];
	// 	for (let prop of props) {
	// 		if (!(prop in new_data)) {
	// 			new_data[prop] = [];
	// 		}
	// 		if (day in paired) {
	// 			new_data[prop].push(paired[day][prop]);
	// 		} else if (day_n < num_days) {
	// 			new_data[prop].push(new_data[prop][new_data[prop].length - 1]);
	// 		}
	// 	}
	// }

	new_days = date_range(data.entry_date[0], data.entry_date.length * (extra_days ? 2 : 1));
	new_data = data;

	return {days: new_days, data: new_data};
}
 
let last_added_data = {};

function reset_predicted_data_datapoints() {
	chart.data.datasets[index.predicted].data = [];
}

function add_log_predictor(fit) {
	reset_predicted_data_datapoints();
	let func = chart_type == "total" ? predict_log : deriv_log;
	for (let day = 0; day < chart.data.labels.length; day++) {
		chart.data.datasets[index.predicted].data.push(func(fit, day));
	}
	chart.update();
}

function add_lstm_predictor({y}) {
	reset_predicted_data_datapoints();
	for (let day = 0; day < y.length; day++) {
		if (chart_type == "total") {
			chart.data.datasets[index.predicted].data.push(y[day]);
		} else {
			if (day == 0) {
				chart.data.datasets[index.predicted].data.push(y[0]);
			} else {
				chart.data.datasets[index.predicted].data.push(y[day] - y[day - 1]);
			}
		}
	}
	chart.update();
}

function reset_chart_data() {
	for (let i in chart.datasets) {
		chart.datasets[i].data = [];
	}
}

function redraw_chart() {
	set_chart_data({...last_added_data.data, entry_date: last_added_data.days.slice(0, last_added_data.data.total.length)});
}

function set_chart_data(data) {
	reset_chart_data();
	let datasets = chart.data.datasets;

	// now, we go through each date and fill in any missing dates with a filler
	let show_predictions = predictor_type != "none";
	let fixed = fix_data(data, show_predictions);
	last_added_data = fixed;

	chart.data.labels = fixed.days;

	let props = ['total', 'deaths', 'recovered'];
	if (chart_type == "daily-change") {
		props = ['dtotal', 'ddeaths', 'drecovered'];
	}

	if (predictor_type == "log") {
		$.post(
			// DEBUG MARKER
			"//prediction-dot-tactile-welder-255113.uc.r.appspot.com/predict/log",
			//"//localhost:5050/predict/log",
			//"//coronavision-ml.herokuapp.com/predict/log",
			{
				X: fixed.days.slice(fixed.data.total.length).join(" "),
				Y: fixed.data.total.join(" ")
			},
			(log_predictor_json) => {
				// make sure they didn't change the settings
				if (predictor_type == "log") {
					predictor_type = "log";
					add_log_predictor(log_predictor_json);
				}
			},
			"json"
		);
	} 
	else if (predictor_type == "lstm") {
		$.post(
			// DEBUG MARKER
			"//prediction-dot-tactile-welder-255113.uc.r.appspot.com/predict/lstm",
			// "//localhost:5050/predict/lstm",
			//"//coronavision-ml.herokuapp.com/predict/lstm",
			{
				X: fixed.days.slice(fixed.data.total.length).join(" "),
				Y: fixed.data.total.join(" ")
			},
			(lstm_predictor_json) => {
				// make sure they didn't change the settings
				if (predictor_type == "lstm") {
					predictor_type = "lstm";
					add_lstm_predictor(lstm_predictor_json);
				}
			},
			"json"
		);
	}
	
	for (let i in props) {
		datasets[i].data = smooth_data(fixed.data[props[i]], chart_smoothing);
	}

	chart.update()
}

function date_range(start_date, num_days) {
	let ret = [];
	let d = new Date(start_date);
	for (let i = 0; i < num_days; i++) {
		ret.push(d.toISOString().substring(0, 10));
		d.setTime(d.getTime() + 1000 * 60 * 60 * 24);
	}
	return ret;
}

function deriv_log(fit, x) {
	return (predict_log(fit, x + 0.001) - predict_log(fit, x)) / 0.001; 
}

function predict_log(fit, x) {
	return fit.MAX/(1 + Math.exp(-(x - fit.T_INF)/fit.T_RISE));
}

function smooth_data(array, smoothing) {
	if (typeof(array) == "undefined") {
		return array;
	}

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
	
	let admin0 = CORONA_GLOBALS.admin0;
	let admin1 = CORONA_GLOBALS.admin1;
	let admin2 = CORONA_GLOBALS.admin2;
	
	let label = generate_name(admin0, admin1, admin2);

	let params = {
		admin0: admin0,
		admin1: admin1,
		admin2: admin2,
		world: "World"
	}
	
	waiting = params;

	$.getJSON(
		"/cases/totals_sequence",
		params,
		function(data) {
			if (waiting == params) {
				set_chart_data(data);
				chart.options.title.text = 'Cases in: ' + label;
				chart.update();
			}
		}
	)
}