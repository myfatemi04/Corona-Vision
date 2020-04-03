var map = null;
var active_markers = [];
var markers_by_country = {};
var locations = {};
var location_autocomplete = null;
var marker_cluster = null;
var most_recent_person = null;

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

function format_data(label, data) {
	let formatted = `<b>${label}</b><br/>`
	+ `Confirmed: ${data.confirmed} (+${data.dconfirmed})<br/>`
	+ `Recovered: ${data.recovered} (+${data.drecovered})<br/>`
	+ `Dead: ${data.dead} (+${data.ddead})<br/>`
	+ `Active: ${data.active} (+${data.dactive})<br/>`;

	return formatted;
}

function add_country_info(person, entry_date) {
	if (person && person.country) {
		let xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				let data = JSON.parse(this.responseText)[0];
				if (data)
					$("#country-info")[0].innerHTML = format_data(`Country: ${data.country}`, data);	
				else
					$("#country-info")[0].innerHTML = '';
			}
		}
		xhr.open("GET", `/cases/totals?country=${person.country}&date=${entry_date}`)
		xhr.send()
	} else {
		$("#country-info")[0].innerHTML = '';
	}
}

function add_county_info(person, entry_date) {
	if (person && person.admin2) {
		$("#county-info")[0].innerHTML = format_data(`County: ${person.admin2}`, person);	
	} else {
		$("#county-info")[0].innerHTML = '';
	}
}

function add_province_info(person, entry_date) {
	if (person && person.province) {
		let xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				let data = JSON.parse(this.responseText)[0];
				if (data)
					$("#province-info")[0].innerHTML = format_data(`State: ${data.province}`, data);
				else
					$("#province-info")[0].innerHTML = '';
			}
		}
		xhr.open("GET", `/cases/totals?country=${person.country}&province=${person.province}&date=${entry_date}`)
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

			let entry_date = $("#date")[0].value;
			add_country_info(most_recent_person, entry_date);
			add_province_info(most_recent_person, entry_date);
			add_county_info(most_recent_person, entry_date);
			let county_found = false;
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
					if (most_recent_person) {
						if (person.country == most_recent_person.country &&
							person.province == most_recent_person.province &&
							person.admin2 == most_recent_person.admin2) {
								add_county_info(person, entry_date);
								county_found = true;
							}
					}
					
					
					new_marker.addListener('click', function() {
						let entry_date = $("#date")[0].value;
						add_country_info(person, entry_date);
						add_province_info(person, entry_date);
						add_county_info(person, entry_date);
						most_recent_person = person;
					});
					
					new_marker.setMap(map);
					active_markers.push(new_marker);
				}
			}

			if (!county_found) {
				$("#county-info")[0].innerHTML = '';
			}
		}
	};
	
	let bounds = map.getBounds();
	let ne = bounds.getNorthEast();
	let sw = bounds.getSouthWest();
	let entry_date = $("#date")[0].value;
	let request_content = `?ne_lat=${ne.lat()}&ne_lng=${ne.lng()}&sw_lat=${sw.lat()}&sw_lng=${sw.lng()}&date=${entry_date}`;
	xhr.open("GET", "/cases/box" + request_content);
	xhr.send();
}