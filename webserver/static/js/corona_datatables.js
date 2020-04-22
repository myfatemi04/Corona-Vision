let by_country = {};
let by_us_state = {};

function filter_table() {
    let filter_key = $("#locationSearch")[0].value;
    for (let child of $("#tablebody")[0].children) {
        if (!child.hasAttribute('data-label')) {
            continue;
        }
        let label = child.getAttribute('data-label');
        if (label.toLowerCase().startsWith(filter_key)) {
            child.style.display = "flex";
        } else {
            child.style.display = "none";
        }
    }
}

function set_country(country) {
    $("#country-selector").val(country);
    $("#country-selector").trigger("change");
}
function set_admin1(admin1) {
    $("#admin1-selector").val(admin1);
    $("#admin1-selector").trigger("change");
}

function set_county(county) {
    $("#county-selector").val(county);
    $("#county-selector").trigger("change");
}

function reload_data() {
    let entry_date = $("#date")[0].value;
    let params = {
        country: CORONA_GLOBALS.country,
        admin1: CORONA_GLOBALS.admin1,
        county: CORONA_GLOBALS.county,
        date: entry_date
    };

    // if any are unspecified, set to all (highest level only, so else if)
    if (params.country == '') {
        params.country = 'all';
    } else if (params.admin1 == '' && params.country != '') {
        params.admin1 = 'all';
    } else if (params.county == '') {
        params.county = 'all';
    }
    $.get(
        "/cases/totals_table",
        params,
        function(result) {
            $("#tablebody")[0].innerHTML = result;
            //by_country[entry_date] = result;
            //show_data(result, level, def);
        }
    );
}
