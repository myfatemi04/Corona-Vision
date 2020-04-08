function update_stats() {
    let entry_date = $("#date")[0].value;
    
    let country = CORONA_GLOBALS.country;
    let province = CORONA_GLOBALS.province;
    let admin2 = CORONA_GLOBALS.admin2;

    $.getJSON(
        "/cases/totals",
        {
            country: country,
            province: province,
            admin2: admin2,
            date: entry_date
        },
        function(data) {
            if (data) {
                $("#stats-info")[0].innerHTML = format_data(generate_name(country, province, admin2), data[0]);
            } else {
                $("#stats-info")[0].innerHTML = '';
            }
        }
    );
}

function init_stats_panel() {
    CORONA_GLOBALS.reload_function = function() {
        update_stats();
    };

    update_stats();
}

function format_data(label, data) {
	let formatted = `
	<div class="lato" style="font-size: 1.5rem; background-color: #212121;">
		<code><b>${label}</b></code><br/>
		<code><b>Confirmed:</b> ${data.confirmed} (+${data.dconfirmed})</code><br/>
		<code><b>Active:</b> ${data.active} (+${data.dactive})</code><br/>
		<code><b>Deaths:</b> ${data.deaths} (+${data.ddeaths})</code><br/>
		<code><b>Recoveries:</b> ${data.recovered} (+${data.drecovered})</code><br/>
	</div>
	`;
	return formatted;
}