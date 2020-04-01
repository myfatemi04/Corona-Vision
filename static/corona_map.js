var map = null;
var active_markers = [];
var markers_by_country = {};
var locations = {};
var location_autocomplete = null;
var marker_cluster = null;

function init_coronamap() {
	map = new google.maps.Map($("#map")[0],
		{
			zoom: 8,
			streetViewControl: false,
			minZoom: 2
		});
	map.addListener("dragend", function() {
		reload_cases();
	});
	map.addListener("zoom_changed", function() {
		reload_cases();
	});
}

function init() {
	get_location();
	init_autocomplete();
}

function init_autocomplete() {
	let map_options = {};
	location_autocomplete = new google.maps.places.Autocomplete($("#location")[0], map_options);
}

function get_location() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(show_location);
	}
}

function show_location(position) {
	let latitude = position.coords.latitude;
	let longitude = position.coords.longitude;
	$("#map")[0].setAttribute("class", "map display-block");
	$("#map-message")[0].setAttribute("class", "display-none");
	let my_location = {
		lat: latitude,
		lng: longitude
	};
	map.setCenter(my_location);
	setTimeout(reload_cases, 1000);
}

function remove_previous_markers() {
	for (let marker of active_markers) {
		marker.setMap(null);
	}
	active_markers = [];
	markers_by_country = {};
}

function find_cases() {
	$("#map")[0].setAttribute("class", "map display-block");
	$("#map-message")[0].setAttribute("class", "display-none");
	
	if (typeof(location_autocomplete.getPlace()) !== 'undefined') {
		let loc = location_autocomplete.getPlace().geometry.location;
		map.setCenter(loc);
	}
	
	setTimeout(reload_cases, 1000);
}

function get_icon_url_based_on_severity(num_cases) {
	let base_url = "http://maps.google.com/mapfiles/ms/icons/";
	if (num_cases < 0) {
		return base_url + "blue.png"
	}
	let log_n = Math.log(num_cases)/Math.log(2);
	let color = "blue";
	if (log_n < 4) color = "blue";
	else if (log_n < 8) color = "green";
	else if (log_n < 12) color = "yellow";
	else if (log_n < 16) color = "orange";
	else color = "red";
	return base_url + color + ".png";
}

function add_country_info(person, entry_date) {
	if (person.country) {
		let xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				let parsed_data = JSON.parse(this.responseText);
				$("#country-info")[0].innerHTML = `<b>Country info: ${person.country}</b><br/>Confirmed: ${parsed_data.total_confirmed}<br/>Recovered: ${parsed_data.total_recovered}<br/>Dead: ${parsed_data.total_dead}<br/>Active: ${parsed_data.total_active}`;
			}
		}
		xhr.open("GET", `/cases/country_total/${person.country}/${entry_date}`)
		xhr.send()
	}
}

function add_county_info(person, entry_date) {
	if (person.admin2) {
		$("#county-info")[0].innerHTML = `<b>County Info</b><br/>${person.admin2}<br/>Confirmed: ${person.confirmed}<br/>Recovered: ${person.recovered}<br/>Dead: ${person.dead}. Active: ${person.active}`;	
	} else {
		$("#county-info")[0].innerHTML = '';
	}
}

function add_province_info(person, entry_date) {
	if (person.province) {
		let xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				let parsed_data = JSON.parse(this.responseText);
				$("#province-info")[0].innerHTML = `<b>State info: ${person.province}</b><br/>Confirmed: ${parsed_data.total_confirmed}<br/>Recovered: ${parsed_data.total_recovered}<br/>Dead: ${parsed_data.total_dead}<br/>Active: ${parsed_data.total_active}`;
			}
		}
		xhr.open("GET", `/cases/province_total/${person.province}/${person.country}/${entry_date}`)
		xhr.send()
	} else {
		$("#province-info")[0].innerHTML = '';
	}
}

function reload_cases() {
	let xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			remove_previous_markers();
			for (let person of JSON.parse(this.responseText)) {
				if (person.confirmed > 0 && person.country) {
					let new_marker = new google.maps.Marker({
						position: {
							lat: person.latitude,
							lng: person.longitude
						},
						title: `[${person.country} ${person.province} ${person.admin2}]: Confirmed: ${person.confirmed}. Recovered: ${person.recovered}. Dead: ${person.dead}. Active: ${person.active}.`,
						icon: get_icon_url_based_on_severity(person.active)
					});
					
					new_marker.addListener('click', function() {
						let entry_date = $("#date")[0].value;
						add_country_info(person, entry_date);
						add_province_info(person, entry_date);
						add_county_info(person, entry_date);
					});
					
					new_marker.setMap(map);
					active_markers.push(new_marker);
				}
			}
		}
	};
	
	let bounds = map.getBounds();
	let ne = bounds.getNorthEast();
	let sw = bounds.getSouthWest();
	let entry_date = $("#date")[0].value;
	let exclude_level = "none";
	if (map.zoom < 4) {
		exclude_level = "province";
	} else if (map.zoom < 8) {
		exclude_level = "admin2";
	}
	let request_content = `?ne_lat=${ne.lat()}&ne_lng=${ne.lng()}&sw_lat=${sw.lat()}&sw_lng=${sw.lng()}&date=${entry_date}&exclude_level=${exclude_level}`;
	xhr.open("GET", "/cases" + request_content);
	xhr.send();
}