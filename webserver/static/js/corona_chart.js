let index = {
	total: 0,
	deaths: 1,
	recovered: 2,
	predicted: 3
};

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

function download_canvas() {
	let url = $("#chart")[0].toDataURL("image/png;base64");
	let filename = 'COVID19_Chart.png';

	$("#download-chart")[0].href = url;
	$("#download-chart")[0].setAttribute("download", filename);
	$("#download-chart")[0].click();
}

function smoothData(array, smoothing) {
	if (typeof(smoothing) == "string") {
		smoothing = parseInt(smoothing);
	}

	if (typeof(array) == "undefined") {
		return array;
	}
	
	// smoothing is too high
	if (smoothing > array.length - 1) {
		smoothing = array.length - 1;
	}
	
	// now, we use a map function
	return array.map((value, index) => {
		// at a certain index, take the values N days before and N days after
		let left = Math.max(index - smoothing, 0);
		let right = Math.min(index + smoothing + 1, array.length);
		let values = array.slice(left, right);
		
		let sum = values.reduce((a, b) => (a + b));
	
		let missing_left = left - (index - smoothing);
		let missing_right = (index + smoothing + 1) - right;
	
		sum += missing_left * array[0];
		sum += missing_right * array[array.length - 1];
	
		return sum / (2 * smoothing + 1);
	});
}

function redrawChart(chart) {
	let props = [];
	if (chart.dataType == "daily-change") props = ['dtotal', 'ddeaths', 'drecovered'];
	else props = ['total', 'deaths', 'recovered'];
	
	for (let i in props) {
		chart.data.datasets[i].data = smoothData(chart.originalData[props[i]], chart.smoothing);
	}
	chart.update();
	setTimeout(chart.update, 250); // for some reason, the charts don't load immediately on mobile
}

function initChartOptions(chart) {
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
			chart.dataType = $("select[name=chart-type]").val()
			redrawChart(chart);
        }
    );
	
	$("input#smoothing").change(
		function() {
			chart.smoothing = parseInt($("input#smoothing").val());
			redrawChart(chart);
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

// if (predictor_type == "conv") {
// 	$.get(
// 		"//prediction-dot-tactile-welder-255113.uc.r.appspot.com/predict/conv",
// 		// "//localhost:5050/predict/conv",
// 		{ country: country, province: province, county: county },
// 		(conv_predictor_json) => {
// 			// make sure they didn't change the settings
// 			if (predictor_type == "conv") {
// 				predictor_type = "conv";
// 				add_conv_predictor(conv_predictor_json);
// 			}
// 		},
// 		"json"
// 	);
// }

// chart.data.labels = data.entry_date;
// for (let i in props) {
// 	chart.data.datasets[i].data = data[props[i]];
// }

function deriv_log(fit, x) {
	return (predict_log(fit, x + 0.001) - predict_log(fit, x)) / 0.001; 
}

function predict_log(fit, x) {
	return fit.MAX/(1 + Math.exp(-(x - fit.T_INF)/fit.T_RISE));
}
