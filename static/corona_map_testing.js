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
			streetViewControl: false
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
	let log_n = Math.log(num_cases)/Math.log(2);
	let color = "blue";
	if (log_n < 4) color = "blue";
	else if (log_n < 8) color = "green";
	else if (log_n < 12) color = "yellow";
	else if (log_n < 16) color = "orange";
	else color = "red";
	return base_url + color + ".png";
}

function load_country_total(country, datestr) {
	let xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let parsed_data = JSON.parse(this.responseText);
			console.log(parsed_data);
			$("#country-info")[0].innerHTML = `<b>Country info: ${country}</b><br/>Confirmed: ${parsed_data.total_confirmed}<br/>Recovered: ${parsed_data.total_recovered}<br/>Dead: ${parsed_data.total_dead}<br/>Active: ${parsed_data.total_active}`;
		}
	}
	xhr.open("GET", `/cases/total/${country}/${datestr}`)
	xhr.send()
}

function save_location(country, state, county) {
	$.getJSON(
		"http://nominatim.openstreetmap.org/search/?format=json"
		+ "&country=" + country
		+ "&state=" + state
		+ "&county=" + county,
		function(places) {
			place = places[0];
			place_lat = place['lat']
			place_lng = place['lon']
			if (!locations.hasOwnProperty(country)) {
				locations[country] = {
					"states": {}
				}
			}
			if (!locations[country]['states'].hasOwnProperty(state)) {
				locations[country]['states'][state] = {
					"counties": {}
				}
			}
			locations[country]['states'][state]['counties'][county] = {
				"lat": place_lat,
				"lng": place_lng
			};
		}
	);
}

function reload_cases() {
	let xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			remove_previous_markers();
			for (let person of JSON.parse(this.responseText)) {
				if (!markers_by_country.hasOwnProperty(person.country)) {
					//save_location(person.country, "", "");
					markers_by_country[person.country] = {
						"states": {},
						"total": {
							"confirmed": 0,
							"recovered": 0,
							"dead": 0,
							"active": 0
						}
					};
				}
				
				markers_by_country[person.country]['total']['confirmed'] += person.confirmed;
				markers_by_country[person.country]['total']['recovered'] += person.recovered;
				markers_by_country[person.country]['total']['dead'] += person.dead;
				markers_by_country[person.country]['total']['active'] += person.active;
				
				let new_marker = new google.maps.Marker({
					position: {
						lat: person.latitude,
						lng: person.longitude
					},
					title: `[${person.country}]: Confirmed: ${markers_by_country[person.country]['total']['confirmed']}. Recovered: ${markers_by_country[person.country]['total']['recovered']}. Dead: ${markers_by_country[person.country]['total']['dead']}. Active: ${markers_by_country[person.country]['total']['active']}.`,
					icon: get_icon_url_based_on_severity(person.active)
				});
				
				new_marker.addListener('click', function() {
					let marker_info = $("#marker-info")[0];
					marker_info.innerHTML = `<b>Region Info</b><br/>Region: whole country<br/>Confirmed: ${person.confirmed}<br/>Recovered: ${person.recovered}<br/>Dead: ${person.dead}. Active: ${person.active}`;
					load_country_total(person.country, $("#date")[0].value);
				});
				
				markers_by_country[person.country]['marker'] = new_marker;
				if (map.zoom <= 4) {
					active_markers.push(new_marker);
					new_marker.map = map;
				}
				
				if (person.province) {
					if (!markers_by_country[person.country]['states'].hasOwnProperty(person.province)) {
						save_location(person.country, person.province, "");
						markers_by_country[person.country]['states'][person.province] = {
							"counties": {},
							"total": {
								"confirmed": 0,
								"recovered": 0,
								"dead": 0,
								"active": 0
							}
						}
					}
					
					markers_by_country[person.country]['states'][person.province]['total']['confirmed'] += person.confirmed;
					markers_by_country[person.country]['states'][person.province]['total']['recovered'] += person.recovered;
					markers_by_country[person.country]['states'][person.province]['total']['dead'] += person.dead;
					markers_by_country[person.country]['states'][person.province]['total']['active'] += person.active;
					
					let new_marker = new google.maps.Marker({
						position: {
							lat: person.latitude,
							lng: person.longitude
						},
						title: `[${person.country}] ${person.province}: Confirmed: ${person.confirmed}. Recovered: ${person.recovered}. Dead: ${person.dead}. Active: ${person.active}.`,
						icon: get_icon_url_based_on_severity(person.active)
					});
					
					new_marker.addListener('click', function() {
						let marker_info = $("#marker-info")[0];
						marker_info.innerHTML = `<b>Region Info</b><br/>Region: ${person.province}<br/>Confirmed: ${person.confirmed}<br/>Recovered: ${person.recovered}<br/>Dead: ${person.dead}. Active: ${person.active}`;
						load_country_total(person.country, $("#date")[0].value);
					});
					
					markers_by_country[person.country]['states'][person.province]['marker'] = new_marker;
					if (4 < map.zoom <= 6) {
						active_markers.push(new_marker);
						new_marker.map = map;
					}
					
					if (person.admin2) {
						save_location(person.country, person.province, person.admin2);
						markers_by_country[person.country]['states'][person.province]['counties'][person.admin2] = {
							"total": {
								"confirmed": 0,
								"recovered": 0,
								"dead": 0,
								"active": 0
							}
						};
						
						markers_by_country[person.country]['states'][person.province]['counties'][person.admin2]['total']['confirmed'] += person.confirmed;
						markers_by_country[person.country]['states'][person.province]['counties'][person.admin2]['total']['recovered'] += person.recovered;
						markers_by_country[person.country]['states'][person.province]['counties'][person.admin2]['total']['dead'] += person.dead;
						markers_by_country[person.country]['states'][person.province]['counties'][person.admin2]['total']['active'] += person.active;
						
						let new_marker = new google.maps.Marker({
							position: {
								lat: person.latitude,
								lng: person.longitude
							},
							title: `[${person.country}] ${person.province}: Confirmed: ${person.confirmed}. Recovered: ${person.recovered}. Dead: ${person.dead}. Active: ${person.active}.`,
							icon: get_icon_url_based_on_severity(person.active)
						});
						
						new_marker.addListener('click', function() {
							let marker_info = $("#marker-info")[0];
							marker_info.innerHTML = `<b>Region Info</b><br/>Region: ${person.admin2} ${person.province}<br/>Confirmed: ${person.confirmed}<br/>Recovered: ${person.recovered}<br/>Dead: ${person.dead}. Active: ${person.active}`;
							load_country_total(person.country, $("#date")[0].value);
						});
						
						markers_by_country[person.country]['states'][person.province]['counties'][person.admin2]['marker'] = new_marker;
						if (6 < map.zoom) {
							active_markers.push(new_marker);
							new_marker.map = map;
						}

					}
				}
			}
		}
	};
	
	let bounds = map.getBounds();
	let ne = bounds.getNorthEast();
	let sw = bounds.getSouthWest();
	let entry_date = $("#date")[0].value;
	let request_content = `?ne_lat=${ne.lat()}&ne_lng=${ne.lng()}&sw_lat=${sw.lat()}&sw_lng=${sw.lng()}&date=${entry_date}`;
	xhr.open("GET", "/cases" + request_content);
	xhr.send();
}