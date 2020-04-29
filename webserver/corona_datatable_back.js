const countryjs = require('countryjs');
const COLORS = require("./static/js/colors.js");

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
    let innerText = '-';

    if (number != 0 && typeof number != 'undefined') {
        if (options.hasOwnProperty("digits")) innerText = nFormatter(number, options.digits);
        else innerText = number;

        if (options.source) {
            innerText = `<a href='${options.source}' style='color: inherit; text-decoration: underline;'>` + innerText + `</a>`;
        }
    }
    
    let color = options.color || COLORS.fg;
    let flex = options.flex || 2;
    let fontWeight = options.fontWeight || 800;

    let style = `color: ${color}; flex: ${flex}; font-weight: ${fontWeight};`;
    style += options.style || "";

    return `<td class="mx-1" style='${style}'>${innerText}</td>`;
}

let ico = ""; // <i class="fas fa-angle-right"></i>

function set_country_link(entry_date, country) {
    return `<a class='country-link' href='?date=${entry_date}&country=${country}'>${country} ${ico}</a>`;
}

function set_province_link(entry_date, country, province) {
    return `<a class='country-link' href='?date=${entry_date}&country=${country}&province=${province}'>${province} ${ico}</a>`;
}

function set_county_link(entry_date, country, province, county) {
    return `<a class='country-link' href='?date=${entry_date}&country=${country}&province=${province}&county=${county}';>${county} ${ico}</a>`
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
        if (country == '') { label_prop = 'country'; label_default = 'World'; }

        // if the province isn't specified, we are listing provinces
        else if (province == '') { label_prop = 'province'; label_default = country; }

        // if the county isn't specified, we are listing county
        else if (county == '') { label_prop = 'county'; label_default = province; }

        // if all are specified, we are listing a single entry
        else { label_prop = ''; label_default = county; }

        data.sort((a, b) => (a.total > b.total) ? -1 : 1)
        
        let backText = `<i class="fas fa-angle-double-left"></i> Back`
        let deselect_country_link = `<a href="?date=${entry_date}">${backText}</a>`;
        let deselect_province_link = `<a href="?date=${entry_date}&country=${country}">${backText}</a>`;
        let deselect_county_link = `<a href="?date=${entry_date}&country=${country}&province=${province}">${backText}</a>`;

        let html = "";
        let go_back_link = '';
        if (country != '' && country != 'all') {
            go_back_link = `${(province == '' ? deselect_country_link : (county == '' ? deselect_province_link : deselect_county_link))}`;
        }

        let i = 0;
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

            let tests_mil = 0;

            if (label_prop == 'country') {
                let countryInfo = countryjs.info(label, "name");
                    if (typeof countryInfo != 'undefined') {
                    let population = countryInfo['population'];
                    let area = countryInfo['area'];
                    if (population) {
                        let mils = population / 1000000;
                        tests_mil = (datapoint.tests/mils).toFixed(0);
                    }
                }
            }

            let table_cols = [
                //!label ? go_back_link : i
                {number: i, flex: 1, color: COLORS.fg},
                {number: label_link, color: COLORS.link, flex: 4},
                {number: datapoint.total, source: datapoint.source_total, color: COLORS.total},
                {number: datapoint.dtotal > 0 ? datapoint.dtotal : ``, source: datapoint.source_total, color: COLORS.total},
                {number: datapoint.recovered, color: COLORS.recovered, source: datapoint.source_recovered},
                {number: datapoint.deaths, color: COLORS.deaths, source: datapoint.source_deaths},
                // {number: datapoint.serious, color: COLORS.serious, source: datapoint.source_serious},
                {number: datapoint.tests, color: COLORS.tests, source: datapoint.source_tests}
            ];

            if (label_prop == "country") {
                table_cols.push({number: tests_mil, color: COLORS.tests});
            }

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