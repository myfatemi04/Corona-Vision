var my_location = null;
var map = null;
var markers = [];
var location_autocomplete = null;
var marker_cluster = null;

function init_coronamap() {
	map = new google.maps.Map($("#map")[0],
		{
			zoom: 8,
			center: my_location,
			streetViewControl: false
		});
	map.addListener("dragend", function() {
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
	my_location = {
		lat: latitude,
		lng: longitude
	};
	map.setCenter(my_location);
	setTimeout(reload_cases, 1000);
}

function remove_previous_markers() {
	for (let marker of markers) {
		marker.setMap(null);
	}
	markers = [];
}

function find_cases() {
	$("#map")[0].setAttribute("class", "map display-block");
	$("#map-message")[0].setAttribute("class", "display-none");
	map.setCenter(loc);
	reload_cases();
}

function reload_cases() {
	
	let xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			//remove_previous_markers();
			for (let person of JSON.parse(this.responseText)) {
				let new_marker = new google.maps.Marker({
					position: {
						lat: person.latitude,
						lng: person.longitude
					},
					map: map,
					title: `${person.location}: Confirmed: ${person.confirmed}. Recovered: ${person.recovered}. Dead: ${person.dead}`,
					label: (person.confirmed + "")
				});
				let found_marker = false;
				for (let marker of markers) {
					if (marker.position.lat() == new_marker.position.lat() && marker.position.lng() == new_marker.position.lng()) {
						found_marker = true;
						break;
					}
				}
				if (!found_marker)
					markers.push(new_marker);
			}
		}
	};
	
	let bounds = map.getBounds();
	let ne = bounds.getNorthEast();
	let sw = bounds.getSouthWest();
	let request_content = `?ne_lat=${ne.lat()}&ne_lng=${ne.lng()}&sw_lat=${sw.lat()}&sw_lng=${sw.lng()}`;
	xhr.open("GET", "/cases" + request_content);
	xhr.send();
}