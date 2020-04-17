const sql = require('./corona_sql');

let country_list = [];
let province_list = {};

let COLORS = {
    confirmed: "#fcba03",
    recovered: "#34eb4f",
    deaths: "#eb3d34",
    active: "#eb8c34",
    tests: "#3440eb",
    serious: "#fc8003"
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

    if (number != 0 && typeof number != 'undefined') {
        if (options.hasOwnProperty("digits")) numberString = nFormatter(number, options.digits);
        else numberString = number;
        if (options.hasOwnProperty("denom") && options.denom != 0) {
            let numer = number;
            if (options.hasOwnProperty("customNumer")) {
                numer = options.customNumer;
            }
            let percent = (100 * numer / options.denom).toFixed(1);
            percentString = "(" + percent + "%)";
        }
    }
    
    let color = options.color || "#f5f5f5";
    let flex = options.flex || "2";
    let fontWeight = options.fontWeight || 800;

    let style = `color: ${color}; flex: ${flex}; font-weight: ${fontWeight};`;
    style += options.style || "";

    if ("source" in options && options.source) {
        return `<td class="mx-1" style='${style}'><a href='${options.source}' style='color: inherit; text-decoration: underline;'>${numberString} ${percentString}</a></td>`;
    }


    return `<td class="mx-1" style='${style}'>${numberString} ${percentString}</td>`;
}

let ico = ""; // <i class="fas fa-angle-right"></i>

function set_country_link(label) {
    return `<a style="color: #3657ff;" href='javascript:set_country("${label}")';>${label} ${ico}</a>`;
}

function set_province_link(label) {
    return `<a style="color: #3657ff;" href='javascript:set_province("${label}")';>${label} ${ico}</a>`;
}

function set_admin2_link(label) {
    return `<a style="color: #3657ff;" href='javascript:set_admin2("${label}")';>${label} ${ico}</a>`
}

let deselect_country_link = `<a href="javascript:set_country('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;
let deselect_province_link = `<a href="javascript:set_province('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;
let deselect_admin2_link = `<a href="javascript:set_admin2('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;

module.exports = {
    // load_country_list: () => {
    //     sql.sql.query("select distinct country from datapoints where entry_date='live' and province != '';", (err, results) => {
    //         for (let row of results) {
    //             let country = row.country;
    //             country_list.push(country);
    //             province_list[country] = [];
    //             sql.sql.query("select distinct province from datapoints where entry_date='live' and country = '" + country + "' and admin2 != ''", (err, results) => {
    //                 for (let province_row of results) {
    //                     let province = province_row.province;
    //                     province_list[country].push(province);
    //                 }
    //             });
    //         }
    //     });
    // },
    make_rows: (data, country, province, admin2) => {
        // if the country isn't specified, we are listing countries
        if (country == 'all' || country == '') { label_prop = 'country'; label_default = 'World'; }

        // if the province isn't specified, we are listing provinces
        else if (province == 'all' || province == '') { label_prop = 'province'; label_default = country; }

        // if the admin2 isn't specified, we are listing admin2
        else if (admin2 == 'all' || admin2 == '') { label_prop = 'admin2'; label_default = province; }

        // if all are specified, we are listing a single entry
        else { label_prop = ''; label_default = admin2; }

        data.sort((a, b) => (a.confirmed > b.confirmed) ? -1 : 1)

        let i = 0;

        let html = "";
        if (country != '' && country != 'all') {
            html = `
            <tr>
                <td class="mx-1" style="flex: 1;"></td>
                <td class="mx-1" style="flex: 2;">
                    ${(province == '' || province == 'all' ? deselect_country_link : (admin2 == '' || admin2 == 'all' ? deselect_province_link : deselect_admin2_link))}
                </td>
            </tr>`;
        }

        for (let datapoint of data) {
            let label = datapoint[label_prop];
            
            let label_link = label;
            if (label && label != label_default) {
                let label = datapoint[label_prop];
                if (label_prop == 'country') {
                    // if (country_list.includes(label)) {
                    //     label_link = set_country_link(label);
                    // }
                    label_link = set_country_link(label);
                } else if (label_prop == 'province') {
                    // if (country in province_list && province_list[country].includes(label)) {
                    //     label_link = set_province_link(label);
                    // }
                    label_link = set_province_link(label);
                } else if (label_prop == 'admin2') {
                    label_link = set_admin2_link(label);
                } else {
                    label_link = label;
                }
                i += 1;
            } else {
                label_link = label_default;
            }

            let table_cols = [
                {number: i, flex: 1, color: "#f5f5f5"},
                {number: label_link, flex: 4},
                {number: datapoint.confirmed + " (+" + datapoint.dconfirmed + ")", source: datapoint.source_confirmed, color: COLORS.confirmed, flex: 4},
                //{number: datapoint.dconfirmed, color: COLORS.confirmed},
                {number: datapoint.recovered, color: COLORS.recovered, source: datapoint.source_recovered},
                {number: datapoint.deaths, color: COLORS.deaths, source: datapoint.source_deaths},
                //{number: datapoint.ddeaths, denom: datapoint.deaths, color: COLORS.deaths},
                // {number: datapoint.num_tests, digits: 2, color: COLORS.tests},
                {number: datapoint.serious, color: COLORS.serious, source: datapoint.source_serious},
                // {number: "<a href=" + datapoint.source_link + ">Source</a>", style: "flex: 1;"}
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