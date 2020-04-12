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
                for (let prop of ['confirmed', 'recovered', 'deaths', 'dconfirmed', 'serious']) {
                    $("#stats-" + prop)[0].innerHTML = data[prop] == 0 ? "-" : data[prop];
                }
            } else {
                $("#stats-info").hide();
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
