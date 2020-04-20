let by_admin0 = {};
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

function set_admin0(admin0) {
    $("#admin0-selector").val(admin0);
    $("#admin0-selector").trigger("change");
}
function set_admin1(admin1) {
    $("#admin1-selector").val(admin1);
    $("#admin1-selector").trigger("change");
}

function set_admin2(admin2) {
    $("#admin2-selector").val(admin2);
    $("#admin2-selector").trigger("change");
}

function reload_data() {
    let entry_date = $("#date")[0].value;
    let params = {
        admin0: CORONA_GLOBALS.admin0,
        admin1: CORONA_GLOBALS.admin1,
        admin2: CORONA_GLOBALS.admin2,
        date: entry_date
    };

    // if any are unspecified, set to all (highest level only, so else if)
    if (params.admin0 == '') {
        params.admin0 = 'all';
    } else if (params.admin1 == '' && params.admin0 != '') {
        params.admin1 = 'all';
    } else if (params.admin2 == '') {
        params.admin2 = 'all';
    }
    $.get(
        "/cases/totals_table",
        params,
        function(result) {
            $("#tablebody")[0].innerHTML = result;
            //by_admin0[entry_date] = result;
            //show_data(result, level, def);
        }
    );
}
