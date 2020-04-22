let map = null;
let active_markers = [];
let locations = {};
let location_autocomplete = null;
let most_recent_person = null;
let dark_mode_style = [
	{elementType: 'geometry', stylers: [{color: '#242f3e'}]},
	{elementType: 'labels.text.stroke', stylers: [{color: '#242f3e'}]},
	{elementType: 'labels.text.fill', stylers: [{color: '#746855'}]},
	{
		featureType: 'administrative.locality',
		elementType: 'labels.text.fill',
		stylers: [{color: '#d59563'}]
	},
	{
		featureType: 'poi',
		elementType: 'labels.text.fill',
		stylers: [{color: '#d59563'}]
	},
	{
		featureType: 'poi.park',
		elementType: 'geometry',
		stylers: [{color: '#263c3f'}]
	},
	{
		featureType: 'poi.park',
		elementType: 'labels.text.fill',
		stylers: [{color: '#6b9a76'}]
	},
	{
		featureType: 'road',
		elementType: 'geometry',
		stylers: [{color: '#38414e'}]
	},
	{
		featureType: 'road',
		elementType: 'geometry.stroke',
		stylers: [{color: '#212a37'}]
	},
	{
		featureType: 'road',
		elementType: 'labels.text.fill',
		stylers: [{color: '#9ca5b3'}]
	},
	{
		featureType: 'road.highway',
		elementType: 'geometry',
		stylers: [{color: '#746855'}]
	},
	{
		featureType: 'road.highway',
		elementType: 'geometry.stroke',
		stylers: [{color: '#1f2835'}]
	},
	{
		featureType: 'road.highway',
		elementType: 'labels.text.fill',
		stylers: [{color: '#f3d19c'}]
	},
	{
		featureType: 'transit',
		elementType: 'geometry',
		stylers: [{color: '#2f3948'}]
	},
	{
		featureType: 'transit.station',
		elementType: 'labels.text.fill',
		stylers: [{color: '#d59563'}]
	},
	{
		featureType: 'water',
		elementType: 'geometry',
		stylers: [{color: '#17263c'}]
	},
	{
		featureType: 'water',
		elementType: 'labels.text.fill',
		stylers: [{color: '#515c6d'}]
	},
	{
		featureType: 'water',
		elementType: 'labels.text.stroke',
		stylers: [{color: '#17263c'}]
	}
];

let infowindow = null;
let feature_display = "total"; // can be either: total, deaths, recovered, or dtotal
let circle_colors = {
	total: "#de7c21",
	dtotal: "#de7c21",
	deaths: "#f54842",
	recovered: "#39e639"
}

let last_zoom = 2;
let min_radius = 1000;
let is_api_ready = false;

let zoomins = {
	active: 1,
	total: 1,
	recovered: 1,
	deaths: 1,
	dactive: 1,
	dtotal: 1,
	drecovered: 1,
	ddeaths: 1
}

function init_coronamap() {
	map = new google.maps.Map($("#map")[0],
		{
			zoom: 2,
			minZoom: 1,
			center: {
				lat: 20,
				lng: 0
			},
			streetViewControl: false,
			styles: dark_mode_style
		});
	map.addListener("zoom_changed", function() {
		let new_zoom = map.zoom;
		let zoom_scale = Math.pow(last_zoom/new_zoom, 2);
		for (let circle of active_markers) {
			circle.setRadius((circle.getRadius() - min_radius) * zoom_scale + min_radius);
		}

		last_zoom = new_zoom;
	});
	infowindow = new google.maps.InfoWindow({
		content: "",
		backgroundColor: "#212121"
	});

	setTimeout(reload_cases, 500);
}

function init_map() {
	$("select[name=map-display]").change(
		function() {
			feature_display = this.value;
			reload_cases();
		}
	);
}

function init_autocomplete() {
	location_autocomplete = new google.maps.places.Autocomplete($("#location")[0], {});
}

function show_location(position) {
	let latitude = position.coords.latitude;
	let longitude = position.coords.longitude;
	$("#map")[0].setAttribute("class", "map");
	let my_location = {
		lat: latitude,
		lng: longitude
	};
	map.setCenter(my_location);
	setTimeout(reload_cases, 500);
}

function format_infowindow_data(label, data) {
	let formatted = `
	<div class="lato" style="background-color: #212121;">
		<code><b>${label}</b></code><br/>
		<code><b>Confirmed:</b> ${data.total} (+${data.dtotal})</code><br/>
		<code><b>Active:</b> ${data.active} (+${data.dactive})</code><br/>
		<code><b>Deaths:</b> ${data.deaths} (+${data.ddeaths})</code><br/>
		<code><b>Recoveries:</b> ${data.recovered} (+${data.drecovered})</code><br/>
	</div>
	`;
	return formatted;
}

function remove_previous_markers() {
	for (let marker of active_markers) {
		marker.setMap(null);
	}
	active_markers = [];
}

function find_cases() {
	if (typeof(location_autocomplete.getPlace()) !== 'undefined') {
		let loc = location_autocomplete.getPlace().geometry.location;
		map.setCenter(loc);
		map.setZoom(8);
	}
	setTimeout(reload_cases, 500);
}

function calibrate_zoomins(entry_date) {
	$.getJSON(
		'/cases/totals/',
		{
			date: entry_date
		},
		(data) => {
			if (data) {
				data = data[0];
				zoomins.total = data.total/data.total;
				zoomins.active = data.total/data.active;
				zoomins.deaths = data.total/data.deaths;
				zoomins.recovered = data.total/data.recovered;
				zoomins.dtotal = data.total/data.dtotal;
				zoomins.dactive = data.total/data.dactive;
				zoomins.ddeaths = data.total/data.ddeaths;
				zoomins.drecovered = data.total/data.drecovered;
			}
		}
	);
}

function generate_name(country, admin1, county) {
	let l = '';
	if (county) {
		l += county + ", ";
	}
	if (admin1) {
		l += admin1 + ", ";
	}
	if (country) {
		l += country;
	}
	if (!l) {
		return "World";
	}
	return l;
}

function reload_cases() {
	let xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			remove_previous_markers();

			let entry_date = $("#date")[0].value;
			calibrate_zoomins(entry_date);

			if (most_recent_person && most_recent_person.entry_date != entry_date) {
				infowindow.close();
			}

			let feature = feature_display;
			for (let person of JSON.parse(this.responseText)) {
				if (person[feature] > 0) {
					let new_marker = new google.maps.Circle({
						center: {
							lat: person.latitude,
							lng: person.longitude
						},
						strokeColor: circle_colors[feature_display],
						strokeOpacity: 0.8,
						fillColor: circle_colors[feature_display],
						fillOpacity: 0.8,
						map: map,
						radius: min_radius + Math.sqrt(person[feature] * zoomins[feature]) * 4000 / (map.zoom * map.zoom)
					});
					
					new_marker.addListener('click', function(ev) {
						let entry_date = $("#date")[0].value;
						most_recent_person = person;
						infowindow.setContent(`<div class="text-dark">${format_infowindow_data(generate_name(person.country, person.admin1, person.county), person)}</div>`);
						infowindow.setPosition(ev.latLng);
						infowindow.open(map);
						calibrate_zoomins(entry_date);
					});

					active_markers.push(new_marker);
				}
			}
		}
	};
	
	let entry_date = $("#date")[0].value;
	xhr.open("GET", `/cases/date?date=${entry_date}`);
	xhr.send();
}