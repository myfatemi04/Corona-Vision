let index = {
	confirmed: 0,
	deaths: 1,
	recovered: 2,
	lstm_confirmed: 3,
	log_confirmed: 4,
	log_deaths: 5,
	log_recovered: 6
};

let waiting = null;

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
	
	$("select[name=show_predictions]").change(
		function() {
			CORONA_GLOBALS.show_predictions = this.value == "true" ? true : false;
			CORONA_GLOBALS.reload_function();
		}	
	);

	// for (let prop of ['confirmed', 'deaths', 'recovered', 'active']) {
	// 	$("input[name=display-" + prop + "]").change(
	// 		function() {
	// 			chart.data.datasets[index[prop]].hidden = !this.checked;
	// 		}
	// 	);
	// }
	
	$("input#smoothing").change(
		function() {
			CORONA_GLOBALS.smoothing = this.value;
			reload_chart();
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
				label: 'LSTM predicted confirmed',
				backgroundColor: 'lightgoldenrodyellow',
				borderColor: 'lightgoldenrodyellow',
				fill: false,
				data: [],
				lineTension: 0,
				hidden: false
			},
			{
				label: 'Logistic regression predicted confirmed',
				backgroundColor: 'grey',
				borderColor: 'grey',
				fill: false,
				data: [],
				lineTension: 0,
				hidden: false
			},
			// {
			// 	label: 'Logistic regression predicted deaths',
			// 	backgroundColor: 'lightcoral',
			// 	borderColor: 'lightcoral',
			// 	fill: false,
			// 	data: [],
			// 	lineTension: 0,
			// 	hidden: false
			// },
			// {
			// 	label: 'Logistic regression predicted recoveries',
			// 	backgroundColor: 'lightgreen',
			// 	borderColor: 'lightgreen',
			// 	fill: false,
			// 	data: [],
			// 	lineTension: 0,
			// 	hidden: false
			// }
		]
	};
	return new Chart(get_canvas(canvas_id), {
		type: 'line',
		data: data,
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
	let chart = CORONA_GLOBALS.chart;
	chart.options.title.text = 'Loading';
	chart.data.labels = [];
	for (let i = 0; i < chart.data.datasets.length; i++) {
		chart.data.datasets[i].data = [];
	}
	chart.update();
}

// ADD: confirmed cases (predicted)
// ADD: mortality rate (predicted)
// ADD: time to recover (predicted)

function fix_data(data, extra_days) {
	console.log(data);
	let last_date = new Date(data.entry_date[data.entry_date.length - 1]);
	let first_date = new Date(data.entry_date[0]);
	let diff = (last_date.getTime() - first_date.getTime());
	let day_length = 1000 * 60 * 60 * 24;
	let num_days = diff / day_length;
	let paired = {};
	for (let i = 0; i < data.entry_date.length; i++) {
		paired[data.entry_date[i]] = {
			confirmed: data.confirmed[i],
			recovered: data.recovered[i],
			deaths: data.deaths[i],
			dconfirmed: data.dconfirmed[i],
			drecovered: data.drecovered[i],
			ddeaths: data.ddeaths[i]
		};
	}

	let new_days = null;

	if (extra_days)
		new_days = date_range(data.entry_date[0], num_days * 2);
	else
		new_days = date_range(data.entry_date[0], num_days);
	
	let new_data = {};
	let props = ['confirmed', 'deaths', 'recovered', 'dconfirmed', 'ddeaths', 'drecovered'];
	for (let day_n in new_days) {
		let day = new_days[day_n];
		for (let prop of props) {
			if (!(prop in new_data)) {
				new_data[prop] = [];
			}
			if (day in paired) {
				new_data[prop].push(paired[day][prop]);
			} else if (day_n < num_days) {
				new_data[prop].push(new_data[prop][new_data[prop].length - 1]);
			}
		}
	}

	return {days: new_days, data: new_data};
}
 
function add_chart_data(data) {
	reset_chart();
	let chart = CORONA_GLOBALS.chart;
	let raw = {};

	chart.data.labels = data.entry_date;

	let datasets = chart.data.datasets;
	let extra_days = data.entry_date.length;
	
	// now, we go through each date and add the values
	let fixed = fix_data(data, CORONA_GLOBALS.show_predictions);
	chart.data.labels = fixed.days;
	
	let func = CORONA_GLOBALS.chart_type == 'total' ? predict : deriv;
	let pre = CORONA_GLOBALS.chart_type == 'daily-change' ? "d" : "";
	
	let props = ['confirmed', 'deaths', 'recovered'];
	
	for (let prop of props) {
		raw[index[prop]] = fixed.data[pre + prop];
	}
	
	if (CORONA_GLOBALS.show_predictions) {
		// if (pre != 'd') raw[index.lstm_confirmed] = data.fit.confirmed.y;
		// else raw[index.lstm_confirmed] = [];
	
		// iterate through the dates for the predicted data
		//let prop = "confirmed";
	
		for (let prop of ['confirmed']) {
			raw[index[prop] + 4] = [];
			for (let day = 0; day < fixed.days.length; day++) {
				raw[index[prop] + 4].push(func(data.fit[prop], day));
			}
		}
	}

	// NUMBER OF SLOTS FOR DATA
	for (let i in raw) {
		datasets[i].data = smooth_data(raw[i], CORONA_GLOBALS.smoothing);
	}

	last_raw = raw;

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

function deriv(fit, x) {
	return (predict(fit, x + 0.001) - predict(fit, x)) / 0.001; 
}

function predict(fit, x) {
	return fit.MAX/(1 + Math.exp(-(x - fit.T_INF)/fit.T_RISE));
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
	
	waiting = params;

	$.getJSON(
		"/cases/totals_sequence",
		params,
		function(data) {
			if (waiting == params) {
				add_chart_data(data);
				chart.options.title.text = 'Cases in: ' + label;
				chart.update();
				waiting = null;
			}
		}
	)
}