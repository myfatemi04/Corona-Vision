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
	map.addListener("center_changed", function() {
		show_cases(map.center.lat(), map.center.lng());
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
	show_cases(latitude, longitude);
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
	let loc = location_autocomplete.getPlace().geometry.location;
	show_cases(loc.lat(), loc.lng());
	map.setCenter(loc);
}

function show_cases(latitude, longitude) {
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
			//marker_cluster = new MarkerClusterer(map, markers,
            //{imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
		}
	};
	
	if (location_autocomplete !== null) {	
		let place = location_autocomplete.getPlace();
		if (typeof place !== 'undefined') {
			my_location = place.geometry.location;
		}
	}
	
	let cases_url = "/cases/" + latitude + "/" + longitude;
	
	xhr.open("GET", cases_url);
	xhr.send()
}