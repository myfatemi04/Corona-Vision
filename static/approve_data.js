function approve_data(data_id) {
	let xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			$("#message")[0].innerHTML = "";//Approved!<br/>";
			$("#row-" + data_id).remove()
		} else if (this.readyState == 4 && this.status != 200) {
			$("#message")[0].innerHTML = "";//Error<br/>";
		}
	}
	
	xhr.open("POST", "/approve_data");
	xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhr.send(
		"data_id=" + data_id
	);
	
}
