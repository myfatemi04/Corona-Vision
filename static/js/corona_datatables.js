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

function table_col(options) {
    let number = options.number;
    let numberString = '-';
    let percentString = '';
    let color = "#f5f5f5";

    if (options.hasOwnProperty("color")) {
        color = options.color;
    }

    if (number != 0 && typeof number != 'undefined') {
        if (options.hasOwnProperty("digits")) numberString = nFormatter(number, options.digits);
        else numberString = number;
        if (options.hasOwnProperty("denom") && options.denom != 0) {
            let numer = number;
            if (options.hasOwnProperty("customNumer")) {
                numer = options.customNumer;
            }
            let percent = (100 * numer / options.denom).toFixed(CORONA_GLOBALS.DATA_TABLE.percent_digits);
            percentString = "(" + percent + "%)";
        }
    }

    let flex = 1;
    if (options.hasOwnProperty("flex")) {
        flex = options.flex;
    }

    return `<td class="mx-1" style="flex: ${flex}; color: ${color};">${numberString} ${percentString}</td>`;
}

let deselect_country_link = `<a href="javascript:set_country('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;
let deselect_province_link = `<a href="javascript:set_province('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;

function show_data(data, label_prop, label_default) {
    $("#tablebody")[0].innerHTML = '';
    if (CORONA_GLOBALS.country != '') {
        $("#tablebody")[0].innerHTML = `
        <tr>
            <td class="mx-1" style="flex: 0.5;"></td>
            <td class="mx-1" style="flex: 1;">
                ${CORONA_GLOBALS.province == '' ? deselect_country_link : deselect_province_link}
            </td>
        </tr>`;
    }

    data.sort((a, b) => (a.confirmed > b.confirmed) ? -1 : 1)

    let i = 0;

    for (let datapoint of data) {
        let label = datapoint[label_prop];
        if (!label) label = label_default;
        else i += 1;
        
        let label_link = label;
        if (CORONA_GLOBALS.country == '') {
            if (CORONA_GLOBALS.country_list.includes(label)) {
                label_link = set_country_link(label);
            }
        } else if (CORONA_GLOBALS.province == '') {
            if (CORONA_GLOBALS.province_list[CORONA_GLOBALS.country].includes(label)) {
                label_link = set_province_link(label);
            }
        }

        let table_cols = [
            {number: i, flex: 0.5},
            {number: label_link, flex: 2},
            {number: datapoint.confirmed, color: CORONA_GLOBALS.COLORS.confirmed},
            {number: datapoint.dconfirmed, denom: datapoint.confirmed, color: CORONA_GLOBALS.COLORS.confirmed},
            {number: datapoint.recovered, denom: datapoint.confirmed, color: CORONA_GLOBALS.COLORS.recovered},
            {number: datapoint.deaths, denom: datapoint.confirmed, color: CORONA_GLOBALS.COLORS.deaths},
            {number: datapoint.ddeaths, denom: datapoint.deaths, color: CORONA_GLOBALS.COLORS.deaths},
            {number: datapoint.num_tests, customNumer: datapoint.confirmed, denom: datapoint.num_tests, digits: 2, color: CORONA_GLOBALS.COLORS.tests},
            {number: datapoint.serious, denom: datapoint.confirmed, color: CORONA_GLOBALS.COLORS.serious},
            {number: "<a href=" + datapoint.source_link + ">Source</a>"}
        ];

        let tr = `<tr class="datatable-row" data-label="${label}">`;

        for (let col of table_cols) {
            tr += table_col(col);
        }

        tr += "</tr>";
        
        $("#tablebody")[0].innerHTML += tr;
    }
}

function set_country(country) {
    $("#country-selector").val(country);
    $("#country-selector").trigger("change");
}

function set_country_link(label) {
    return `<a style="color: #3657ff;" href='javascript:set_country("${label}")';>${label} <i class="fas fa-angle-right"></i></a>`;
}

function set_province(province) {
    $("#province-selector").val(province);
    $("#province-selector").trigger("change");
}

function set_province_link(label) {
    return `<a style="color: #3657ff;" href='javascript:set_province("${label}")';>${label} <i class="fas fa-angle-right"></i></a>`
}

function go_back_link() {
    return `<a style="color: #3657ff;" href='javascript:set_country("");'>Back</a>`;
}

function reload_data() {
    let entry_date = $("#date")[0].value;
    let params = {
        country: CORONA_GLOBALS.country,
        province: CORONA_GLOBALS.province,
        date: entry_date
    };

    let level = "country";
    let def = "World";
    if (params.country == '') {
        params.country = 'all';
    } else if (params.province == '' && params.country != '') {
        params.province = 'all';
        def = params.country + " (Overall)";
        level = "province";
    } else if (params.province != '' && params.country != '') {
        params.admin2 = 'all';
        def = params.province + " (Overall)";
        level = "admin2";
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
