const sql = require('./corona_sql');

let admin0_list = [];
let admin1_list = {};

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

function set_admin0_link(admin0) {
    return `<a style="color: #3657ff;" href='?country=${admin0}'>${admin0} ${ico}</a>`;
    // return `<a style="color: #3657ff;" href='javascript:set_admin0("${label}")';>${label} ${ico}</a>`;
}

function set_admin1_link(admin0, admin1) {
    return `<a style="color: #3657ff;" href='?country=${admin0}&province=${admin1}'>${admin1} ${ico}</a>`;
}

function set_admin2_link(admin0, admin1, admin2) {
    return `<a style="color: #3657ff;" href='?country=${admin0}&province=${admin1}&admin2=${admin2}';>${admin2} ${ico}</a>`
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

// let deselect_admin0_link = `<a href="javascript:set_admin0('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;
// let deselect_admin1_link = `<a href="javascript:set_admin1('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;
// let deselect_admin2_link = `<a href="javascript:set_admin2('');"><i class="fas fa-angle-double-left"></i> Go back</a>`;

module.exports = {
    // load_admin0_list: () => {
    //     sql.sql.query("select distinct admin0 from datapoints where entry_date='live' and admin1 != '';", (err, results) => {
    //         for (let row of results) {
    //             let admin0 = row.admin0;
    //             admin0_list.push(admin0);
    //             admin1_list[admin0] = [];
    //             sql.sql.query("select distinct admin1 from datapoints where entry_date='live' and admin0 = '" + admin0 + "' and admin2 != ''", (err, results) => {
    //                 for (let admin1_row of results) {
    //                     let admin1 = admin1_row.admin1;
    //                     admin1_list[admin0].push(admin1);
    //                 }
    //             });
    //         }
    //     });
    // },
    format_update_time: format_update_time,
    make_rows: (data, admin0, admin1, admin2) => {
        // if the admin0 isn't specified, we are listing countries
        if (admin0 == 'all' || admin0 == '') { label_prop = 'admin0'; label_default = 'World'; }

        // if the admin1 isn't specified, we are listing admin1s
        else if (admin1 == 'all' || admin1 == '') { label_prop = 'admin1'; label_default = admin0; }

        // if the admin2 isn't specified, we are listing admin2
        else if (admin2 == 'all' || admin2 == '') { label_prop = 'admin2'; label_default = admin1; }

        // if all are specified, we are listing a single entry
        else { label_prop = ''; label_default = admin2; }

        data.sort((a, b) => (a.total > b.total) ? -1 : 1)

        let i = 0;

        let html = "";
        if (admin0 != '' && admin0 != 'all') {
            // html = `
            // <tr>
            //     <td class="mx-1" style="flex: 1;"></td>
            //     <td class="mx-1" style="flex: 2;">
            //         ${(admin1 == '' || admin1 == 'all' ? deselect_admin0_link : (admin2 == '' || admin2 == 'all' ? deselect_admin1_link : deselect_admin2_link))}
            //     </td>
            // </tr>`;
        }

        for (let datapoint of data) {
            let label = datapoint[label_prop];
            
            let label_link = label;
            if (label) {
                let label = datapoint[label_prop];
                if (label_prop == 'admin0') {
                    label_link = set_admin0_link(datapoint.admin0);
                } else if (label_prop == 'admin1') {
                    label_link = set_admin1_link(datapoint.admin0, datapoint.admin1);
                } else if (label_prop == 'admin2') {
                    label_link = set_admin2_link(datapoint.admin0, datapoint.admin1, datapoint.admin2);
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
        return html;
    }
}