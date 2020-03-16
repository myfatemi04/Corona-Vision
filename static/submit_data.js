var location_autocomplete = null;

function init() {
	init_autocomplete();
}

function init_autocomplete() {
	location_autocomplete = new google.maps.places.Autocomplete($("#location")[0])
}

function submit_data() {
	let location = location_autocomplete.getPlace().geometry.location;
	
	let xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			$("#message")[0].innerHTML = "Data successfully submitted!<br/>You can still submit more data.";
			reset_fields();
		} else if (this.readyState == 4 && this.status != 200) {
			$("#message")[0].innerHTML = "There was a problem with the submission";
		}
	}
	
	xhr.open("POST", "/submit_data");
	xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhr.send(
		"location=" + location_autocomplete.getPlace().formatted_address +
		"&latitude=" + location.lat() +
		"&longitude=" + location.lng() +
		"&email=" + $("#email")[0].value +
		"&confirmed=" + $("#confirmed")[0].value +
		"&recovered=" + $("#recovered")[0].value +
		"&dead=" + $("#dead")[0].value
	);
	
}

function reset_fields() {
	$("#email")[0].value = "";
	$("#num_cases")[0].value = "";
	$("#location")[0].value = "";
}