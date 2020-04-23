const sql = require('./corona_sql');

let country_list = [];
let province_list = {};

let COLORS = {
    total: "#fcba03",
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
        if (options.source == "calculated") {
            options.source = "javascript:alert(\"This data is aggregated from more specific sources, e.g. adding up individual state totals\");";
        }
        return `<td class="mx-1" style='${style}'><a href='${options.source}' style='color: inherit; text-decoration: underline;'>${numberString} ${percentString}</a></td>`;
    }


    return `<td class="mx-1" style='${style}'>${numberString} ${percentString}</td>`;
}

let ico = ""; // <i class="fas fa-angle-right"></i>

function set_country_link(entry_date, country) {
    return `<a style="color: #3657ff;" href='?date=${entry_date}&country=${country}'>${country} ${ico}</a>`;
    // return `<a style="color: #3657ff;" href='javascript:set_country("${label}")';>${label} ${ico}</a>`;
}

function set_province_link(entry_date, country, province) {
    return `<a style="color: #3657ff;" href='?date=${entry_date}&country=${country}&province=${province}'>${province} ${ico}</a>`;
}

function set_county_link(entry_date, country, province, county) {
    return `<a style="color: #3657ff;" href='?date=${entry_date}&country=${country}&province=${province}&county=${county}';>${county} ${ico}</a>`
}

function format_update_time(update_time) {
    let diff = Date.now() - update_time;
    let {ms, s, m, h, d} = {ms: diff, s: diff/1000, m: diff/60000, h: diff/3600000, d: diff/86400000}
    if (s < 1) {
        return Math.round(ms) + "ms ago";
    }
    if (m < 1) {
        return Math.round(s) + "s ago";
    }
    if (h < 1) {
        return Math.round(m) + "m ago";
    }
    if (d < 1) {
        return Math.round(h) + "h ago";
    }
    return Math.round(d) + "d ago";
}

module.exports = {
    format_update_time: format_update_time,
    make_rows: (data, country, province, county, entry_date) => {
        // if the country isn't specified, we are listing countries
        if (country == 'all' || country == '') { label_prop = 'country'; label_default = 'World'; }

        // if the province isn't specified, we are listing provinces
        else if (province == 'all' || province == '') { label_prop = 'province'; label_default = country; }

        // if the county isn't specified, we are listing county
        else if (county == 'all' || county == '') { label_prop = 'county'; label_default = province; }

        // if all are specified, we are listing a single entry
        else { label_prop = ''; label_default = county; }

        data.sort((a, b) => (a.total > b.total) ? -1 : 1)

        let i = 0;
        
        let deselect_country_link = `<a href="?date=${entry_date}"><i class="fas fa-angle-double-left"></i> Go back</a>`;
        let deselect_province_link = `<a href="?date=${entry_date}&country=${country}"><i class="fas fa-angle-double-left"></i> Go back</a>`;
        let deselect_county_link = `<a href="?date=${entry_date}&country=${country}&province=${province}"><i class="fas fa-angle-double-left"></i> Go back</a>`;

        let html = "";
        let go_back_link = '';
        if (country != '' && country != 'all') {
            go_back_link = `${(province == '' || province == 'all' ? deselect_country_link : (county == '' || county == 'all' ? deselect_province_link : deselect_county_link))}`;
            html = `
            <tr>
                <td class="mx-1" style="flex: 1;"></td>
                <td class="mx-1" style="flex: 2;">
                    ${go_back_link}
                </td>
            </tr>`;
        }

        for (let datapoint of data) {
            let label = datapoint[label_prop];
            
            let label_link = label;
            if (label) {
                let label = datapoint[label_prop];
                if (label_prop == 'country') {
                    label_link = set_country_link(entry_date, datapoint.country);
                } else if (label_prop == 'province') {
                    label_link = set_province_link(entry_date, datapoint.country, datapoint.province);
                } else if (label_prop == 'county') {
                    label_link = set_county_link(entry_date, datapoint.country, datapoint.province, datapoint.county);
                } else {
                    label_link = label;
                }
                i += 1;
            } else {
                label_link = label_default;
            }

            let table_cols = [
                {number: i, flex: 1, color: "#f5f5f5"},
                {number: format_update_time(datapoint.update_time)},
                {number: label_link, flex: 4},
                {number: datapoint.total + " (+" + datapoint.dtotal + ")", source: datapoint.source_total, color: COLORS.total, flex: 4},
                //{number: datapoint.dtotal, color: COLORS.total},
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
        return {table_rows: html, go_back_link: go_back_link};
    }
}