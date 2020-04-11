const sql = require('./corona_sql');

let country_list = [];
let province_list = {};

let COLORS = {
    confirmed: "#eb7734",
    recovered: "#34eb4f",
    deaths: "#eb3d34",
    active: "#eb8c34",
    tests: "#3440eb",
    serious: "#bf4b49"
};

function nFormatter(num, digits) {
    var si = [
      { value: 1, symbol: "" },
      { value: 1E3, symbol: "k" },
      { value: 1E6, symbol: "M" },
      { value: 1E9, symbol: "G" },
      { value: 1E12, symbol: "T" },
      { value: 1E15, symbol: "P" },
      { value: 1E18, symbol: "E" }
    ];
    var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
    var i;
    for (i = si.length - 1; i > 0; i--) {
      if (num >= si[i].value) {
        break;
      }
    }
    return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
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
            let percent = (100 * numer / options.denom).toFixed(2);
            percentString = "(" + percent + "%)";
        }
    }

    let flex = 1;
    if (options.hasOwnProperty("flex")) {
        flex = options.flex;
    }

    return `<td class="mx-1" style="flex: ${flex}; color: ${color};">${numberString} ${percentString}</td>`;
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

let deselect_country_link = `<a href="javascript:set_country('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;
let deselect_province_link = `<a href="javascript:set_province('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;

module.exports = {
    load_country_list: () => {
        sql.sql.query("select distinct country from datapoints where entry_date='live' and province != '';", (err, results) => {
            for (let row of results) {
                let country = row.country;
                country_list.push(country);
                province_list[country] = [];
                sql.sql.query("select distinct province from datapoints where entry_date='live' and country = '" + country + "' and admin2 != ''", (err, results) => {
                    for (let province_row of results) {
                        let province = province_row.province;
                        province_list[country].push(province);
                    }
                });
            }
        });
    },
    make_rows: (data, entry_date, country, province) => {
        if (country == 'all') { label_prop = 'country'; label_default = 'World'; }
        else if (province == 'all') { label_prop = 'province'; label_default = country; }
        else if (country != '' && province != '') { label_prop = 'admin2'; label_default = province; }

        data.sort((a, b) => (a.confirmed > b.confirmed) ? -1 : 1)

        let i = 0;

        let html = "";
        if (country != '' && country != 'all') {
            html = `
            <tr>
                <td class="mx-1" style="flex: 0.5;"></td>
                <td class="mx-1" style="flex: 1;">
                    ${(province == '' || province == 'all') ? deselect_country_link : deselect_province_link}
                </td>
            </tr>`;
        }

        for (let datapoint of data) {
            let label = datapoint[label_prop];
            if (!label) label = label_default;
            else i += 1;
            
            let label_link = label;

            if (country == '' || country == 'all') {
                if (country_list.includes(label)) {
                    label_link = set_country_link(label);
                }
            } else if (province == '' || province == 'all') {
                if (province_list[country].includes(label)) {
                    label_link = set_province_link(label);
                }
            }

            let table_cols = [
                {number: i, flex: 0.5},
                {number: label_link, flex: 2},
                {number: datapoint.confirmed, color: COLORS.confirmed},
                {number: datapoint.dconfirmed, denom: datapoint.confirmed, color: COLORS.confirmed},
                {number: datapoint.recovered, denom: datapoint.confirmed, color: COLORS.recovered},
                {number: datapoint.deaths, denom: datapoint.confirmed, color: COLORS.deaths},
                {number: datapoint.ddeaths, denom: datapoint.deaths, color: COLORS.deaths},
                {number: datapoint.num_tests, customNumer: datapoint.confirmed, denom: datapoint.num_tests, digits: 2, color: COLORS.tests},
                {number: datapoint.serious, denom: datapoint.confirmed, color: COLORS.serious},
                {number: "<a href=" + datapoint.source_link + ">Source</a>"}
            ];

            let tr = `<tr class="datatable-row" data-label="${label}">`;

            for (let col of table_cols) {
                tr += table_col(col);
            }

            tr += "</tr>";
            
            html += tr;
        }
        return html;
    }
}