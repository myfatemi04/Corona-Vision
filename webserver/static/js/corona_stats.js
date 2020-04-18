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
        function(data_) {
            if (data_) {
                data = data_[0];
                $("#stats-info").show()
                $("#stats-label")[0].innerHTML = generate_name(country, province, admin2)
                for (let prop of ['total', 'recovered', 'deaths', 'dtotal', 'serious', 'num_tests']) {
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
