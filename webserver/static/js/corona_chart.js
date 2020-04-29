function smoothChart(id, smoothing) {
	let chart = charts[id];

	chart.data.labels = chart.originalLabels.slice(smoothing, chart.originalLabels.length - smoothing);
	for (let label in chart.smoothLabels) {
		let index = chart.smoothLabels[label];
		chart.data.datasets[index].data = smoothData(chart.originalData[label], smoothing).slice(smoothing, chart.originalData[label].length - smoothing);
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
		newDates.push(isoDate(current));
	}
	return newDates;
}

function addTrendline(chart, originalIndex, trendlineIndex) {
	if (typeof originalIndex == 'undefined') {
		originalIndex = 0;
	}
	if (typeof trendlineIndex == 'undefined') {
		trendlineIndex = 1;
	}
	let smoothing = 3;
	let smoothedData = smoothData(chart.data.datasets[originalIndex].data, smoothing).slice(3, -3);
	chart.data.datasets[trendlineIndex].data = [undefined, undefined, undefined, ...smoothedData];
	chart.update();
}

function addData(chart, data, datasets) {
	chart.originalData = data;
	chart.originalLabels = data.entry_date;
	chart.data.labels = data.entry_date;

	for (let i in datasets) {
		chart.data.datasets[i].data = data[datasets[i]];
	}
	
	chart.update();
	$(window).trigger('resize');
}

function newChart(selector, datasets) {
	return new Chart($(selector), {
		type: 'line',
		data: {
			labels: [],
			datasets: datasets
		},
		plugins: plugins,
		options: chartStyles
	});
}

let totalsDataset = {
		label: 'Total cases',
		backgroundColor: COLORS.total + "55",
		borderColor: COLORS.total,
		fill: 'origin',
		data: [],
		lineTension: 0
	};

let dtotalsDataset = {
		label: 'Daily total cases',
		backgroundColor: COLORS.total + "55",
		borderColor: COLORS.total,
		fill: 'origin',
		data: [],
		lineTension: 0
	};

let recoveredDataset =
	{
		label: 'Recovered',
		backgroundColor: COLORS.recovered + "55",
		borderColor: COLORS.recovered,
		fill: 'origin',
		data: [],
		lineTension: 0
	};

let deathsDataset =
	{
		label: 'Deaths',
		backgroundColor: COLORS.deaths + "55",
		borderColor: COLORS.deaths,
		fill: 'origin',
		data: [],
		lineTension: 0
	};

let trendDataset =
	{
		label: 'Trendline',
		backgroundColor: "#ffffff55",
		borderColor: "#ffffff",
		fill: 'origin',
		data: [],
		lineTension: 0	
	}

let standardDatasets = [
	totalsDataset,
	recoveredDataset,
	deathsDataset
];

let logisticPredictionDatasets = [
	totalsDataset,
	{
		label: 'Logistic prediction',
		backgroundColor: '#ffffff55',
		borderColor: '#ffffff',
		fill: 'origin',
		data: [],
		lineTension: 0,
		hidden: false
	}
];

let chartStyles = {
	tooltips: {
		mode: 'index',
		intersect: false,
	},
	responsive: true,
	title: {
		display: true,
		text: "Loading...",
		fontColor: COLORS.fg,
		fontSize: 30,
		fontFamily: "Montserrat"
	},
	legend: {
		display: true,
		labels: { fontColor: COLORS.fg }
	},
	hover: {
		mode: 'nearest',
		intersect: true
	},
	scales: {
		xAxes: [
			{
				gridLines: { color: COLORS.fg },
				ticks: { fontColor: COLORS.fg }
			}
		],
		yAxes: [
			{
				gridLines: { color: COLORS.fg },
				ticks: { fontColor: COLORS.fg}
			}
		]
	}
};

let plugins = [{
	beforeDraw: function (chart, easing) {
		var ctx = chart.chart.ctx;

		// ctx.save();
		// ctx.fillStyle = "";
		// ctx.fillRect(0, 0, $("canvas")[0].width, $("canvas")[0].height);
		// ctx.restore();
	}
}];