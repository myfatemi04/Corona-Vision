
let CONFIRMED_IX = 0;
let DEATHS_IX = 1;
let RECOVERED_IX = 2;
let ACTIVE_IX = 3;

let chart_type = 'total';

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
				lineTension: 0
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

function reset_chart(chart) {
	chart.options.title.text = 'Cases';
	chart.data.labels = [];
	for (let i = 0; i < chart.data.datasets.length; i++) {
		chart.data.datasets[i].data = [];
	}
	chart.update();
}

function update_chart(chart, data) {
	reset_chart(chart);
	for (let total of data) {
		chart.data.labels.push(total.entry_date);
		if (chart_type == 'total') {
			chart.data.datasets[CONFIRMED_IX].data.push(total.confirmed);
			chart.data.datasets[DEATHS_IX].data.push(total.deaths);
			chart.data.datasets[RECOVERED_IX].data.push(total.recovered);
			chart.data.datasets[ACTIVE_IX].data.push(total.active);
		} else if (chart_type == 'daily-change') {
			chart.data.datasets[CONFIRMED_IX].data.push(total.dconfirmed);
			chart.data.datasets[DEATHS_IX].data.push(total.ddeaths);
			chart.data.datasets[RECOVERED_IX].data.push(total.drecovered);
			chart.data.datasets[ACTIVE_IX].data.push(total.dactive);
		}
	}
	chart.update()
}

function show_chart(country, province, admin2, label, chart) {
	reset_chart(chart);
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
			update_chart(chart, data);
			chart.options.title.text = 'Cases in: ' + label;
			chart.update();
		}
	)
}