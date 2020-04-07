function update_stats() {
    let entry_date = $("#date")[0].value;
    let xhr = new XMLHttpRequest();
    
    let country = CHART_OPTIONS.country;
    let province = CHART_OPTIONS.province;
    let admin2 = CHART_OPTIONS.admin2;

    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(this.responseText)[0];
            if (data) {
                $("#stats-info")[0].innerHTML = format_data(generate_name(country, province, admin2), data);
            } else {
                $("#stats-info")[0].innerHTML = '';
            }
        }
    }
    xhr.open("GET", `/cases/totals?country=${country}&province=${province}&admin2=${admin2}&date=${entry_date}`)
    xhr.send()
}

function init_stats_panel() {
    CHART_OPTIONS.reload_function = function() {
        update_stats();
        reload_chart();
    };

    update_stats();
}
