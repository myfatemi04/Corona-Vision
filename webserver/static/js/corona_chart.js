function smoothChart(id, smoothing) {
	let chart = charts[id];

	for (let label in chart.smoothLabels) {
		let index = chart.smoothLabels[label];
		chart.data.datasets[index].data = smoothData(chart.originalData[label], smoothing);
	}

	chart.update();
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

function download(id) {
	let url = $("#" + id)[0].toDataURL("image/png;base64");
	let filename = 'COVID19_Chart.png';

	$("#download-chart")[0].href = url;
	$("#download-chart")[0].setAttribute("download", filename);
	$("#download-chart")[0].click();
}

function scale(chart, val) {
	chart.options.scales.yAxes[0].type = val;
	chart.update();
}

function extendDates(dates) {
	let numDays = dates.length;
	let newDates = [...dates];
	let current = dates[numDays - 1];
	if (typeof current == 'string') {
		current = new Date(current);
	}
	for (let i = 0; i < numDays; i++) {
		current.setUTCDate(current.getUTCDate() + 1);
		dates.push(isoDate(current));
	}
	return dates;
}

function addData(chart, data, datasets) {
	chart.originalData = data;
	chart.data.labels = data.entry_date;

	if (typeof datasets == 'undefined') {
		datasets = ['total', 'recovered', 'deaths'];
	}

	for (let i in datasets) {
		chart.data.datasets[i].data = data[datasets[i]];
	}

	setTimeout(() => {chart.update()}, 500);
}

let totalsDataset = {
		label: 'Total cases',
		backgroundColor: COLORS.total,
		borderColor: COLORS.total,
		fill: false,
		data: [],
		lineTension: 0
	};

let recoveredDataset =
	{
		label: 'Recovered',
		backgroundColor: COLORS.recovered,
		borderColor: COLORS.recovered,
		fill: false,
		data: [],
		lineTension: 0
	};

let deathsDataset =
	{
		label: 'Deaths',
		backgroundColor: COLORS.deaths,
		borderColor: COLORS.deaths,
		fill: false,
		data: [],
		lineTension: 0
	};

let standardDatasets = [
	totalsDataset,
	recoveredDataset,
	deathsDataset
];

let logisticPredictionDatasets = {
	labels: [],
	datasets: [
		totalsDataset,
		{
			label: 'Logistic prediction',
			backgroundColor: 'grey',
			borderColor: 'grey',
			fill: false,
			data: [],
			lineTension: 0,
			hidden: false
		}
	]
};

let chartStyles = {
	responsive: true,
	title: {
		display: true,
		text: "Loading...",
		fontColor: "#f5f5f5",
		fontSize: 30,
		fontFamily: "Lato"
	},
	legend: {
		display: true,
		labels: { fontColor: "#f5f5f5" }
	},
	hover: {
		mode: 'nearest',
		intersect: true
	},
	scales: {
		xAxes: [
			{
				gridLines: { color: "#f5f5f5" },
				ticks: { fontColor: "#f5f5f5" }
			}
		],
		yAxes: [
			{
				gridLines: { color: "#f5f5f5" },
				ticks: { fontColor: "#f5f5f5"}
			}
		]
	}
};

let plugins = [{
	beforeDraw: function (chart, easing) {
		var ctx = chart.chart.ctx;

		ctx.save();
		ctx.fillStyle = "#212121";
		ctx.fillRect(0, 0, $("canvas")[0].width, $("canvas")[0].height);
		ctx.restore();
	}
}];