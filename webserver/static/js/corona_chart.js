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
// let conv_predictor = {};

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

function init_chart(admin0, admin1, admin2) {
	init_chart_options(admin0, admin1, admin2);
	load_chart();
}

function init_chart_options(admin0, admin1, admin2) {
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
            load_chart();
        }
    );
	
	$("select[name=show_predictions]").change(
		function() {
			if (this.value == "log") {
				chart.data.datasets[index.predicted].data = [];
				predictor_type = "log";
				redraw_chart(admin0, admin1, admin2);
			} else if (this.value == "conv") {
				chart.data.datasets[index.predicted].data = [];
				predictor_type = "conv";
				redraw_chart(admin0, admin1, admin2);
			} else {
				predictor_type = "none";
				reset_predicted_data_datapoints();
				redraw_chart(admin0, admin1, admin2);
			}
		}	
	);
	
	$("input#smoothing").change(
		function() {
			chart_smoothing = this.value;
			load_chart();
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
				label: 'Logistic prediction',
				backgroundColor: 'grey',
				borderColor: 'grey',
				fill: false,
				data: [],
				lineTension: 0,
				hidden: false
			},
			{
				label: 'Conv. prediction',
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

function add_conv_predictor({y}) {
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

function redraw_chart(admin0, admin1, admin2) {
	set_chart_data({...last_added_data, entry_date: last_added_data.entry_date.slice(0, last_added_data.total.length)}, admin0, admin1, admin2);
}

function set_chart_data(data, admin0, admin1, admin2) {
	reset_chart_data();
	let datasets = chart.data.datasets;

	// now, we go through each date and fill in any missing dates with a filler
	if (predictor_type != "none") {
		data.entry_date = date_range(data.entry_date[0], data.entry_date.length * 2);
	}

	console.log(data);

	last_added_data = data;

	let props = [];
	if (chart_type == "daily-change") props = ['dtotal', 'ddeaths', 'drecovered'];
	else props = ['total', 'deaths', 'recovered'];

	if (predictor_type == "log") {
		$.get(
			"//prediction-dot-tactile-welder-255113.uc.r.appspot.com/predict/log",
			// "//localhost:5050/predict/log",
			{ admin0: admin0, admin1: admin1, admin2: admin2 },
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
	else if (predictor_type == "conv") {
		$.get(
			"//prediction-dot-tactile-welder-255113.uc.r.appspot.com/predict/conv",
			// "//localhost:5050/predict/conv",
			{ admin0: admin0, admin1: admin1, admin2: admin2 },
			(conv_predictor_json) => {
				// make sure they didn't change the settings
				if (predictor_type == "conv") {
					predictor_type = "conv";
					add_conv_predictor(conv_predictor_json);
				}
			},
			"json"
		);
	}
	
	chart.data.labels = data.entry_date;
	for (let i in props) {
		datasets[i].data = smooth_data(data[props[i]], chart_smoothing);
	}

	chart.update()
}

function date_range(start_date, num_days) {
	let ret = [];
	let d = new Date(start_date);
	for (let i = 0; i < num_days; i++) {
		ret.push(d.toISOString().substring(0, 10));
		d.setUTCDate(d.getUTCDate() + 1);
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

function load_chart(admin0, admin1, admin2) {
	let label = admin0 || "World";
	if (admin1) label = admin1 + ", " + label;
	if (admin2) label = admin2 + ", " + label;
	$.getJSON(
		"/cases/totals_sequence",
		{
			admin0: admin0,
			admin1: admin1,
			admin2: admin2
		},
		function(data) {
			set_chart_data(data, admin0, admin1, admin2);
			chart.options.title.text = 'Cases in ' + label;
			chart.update();
		}
	)
}