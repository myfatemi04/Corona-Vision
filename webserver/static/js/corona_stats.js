function update_stats() {
    let entry_date = $("#date")[0].value;
    
    let country = CORONA_GLOBALS.country;
    let admin1 = CORONA_GLOBALS.admin1;
    let county = CORONA_GLOBALS.county;

    $.getJSON(
        "/cases/totals",
        {
            country: country,
            admin1: admin1,
            county: county,
            date: entry_date
        },
        function(data_) {
            if (data_) {
                data = data_[0];
                $("#stats-info").show()
                $("#stats-label")[0].innerHTML = generate_name(country, admin1, county)
                for (let prop of ['total', 'recovered', 'deaths', 'dtotal', 'active', 'serious', 'tests', 'dtests']) {
                    if (("source_" + prop) in data && data["source_" + prop]) {
                        if (data["source_" + prop] == "calculated") {
                            data["source_" + prop] = "javascript:alert('This data is aggregated from more specific sources, e.g. adding up individual state totals');";
                        }
                        $("#stats-" + prop)[0].innerHTML = `<a style="color: inherit; text-decoration: underline;" href="${data['source_' + prop]}">` + (data[prop] == 0 ? "-" : data[prop]) + "</a>";
                    } else {
                        $("#stats-" + prop)[0].innerHTML = data[prop] == 0 ? "-" : data[prop];
                    }
                }
            } else {
                $("#stats-info").hide();
            }
        }
    );
}

function init_stats_panel() {
    update_stats();
}
