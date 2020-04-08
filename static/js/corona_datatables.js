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

function show_data(data, label_prop, label_default) {
    $("#tablebody")[0].innerHTML = '';

    data.sort((a, b) => (a.confirmed > b.confirmed) ? -1 : 1)

    let i = 0;

    for (let datapoint of data) {
        let label = datapoint[label_prop];
        if (!label) label = label_default;

        let cp = (100 * datapoint.dconfirmed/datapoint.confirmed).toFixed(2);
        let rp = (100 * datapoint.drecovered/datapoint.recovered).toFixed(2);
        let dp = (100 * datapoint.ddeaths/datapoint.deaths).toFixed(2);
        if (isNaN(cp)) cp = 0;
        if (isNaN(rp)) rp = 0;
        if (isNaN(dp)) dp = 0;
        
        let dc = `<td class="mx-1" style="flex: 1;">-</td>`;
        if (datapoint.dconfirmed != 0) { 
            dc = `<td class="mx-1" style="flex: 1;">${datapoint.dconfirmed} (${cp}%)</td>`;
        }

        let r = `<td class="mx-1" style="flex: 1;">-</td>`;
        if (datapoint.recovered != 0) { 
            r = `<td class="mx-1" style="flex: 1;">${datapoint.recovered}</td>`;
        }

        let dr = `<td class="mx-1" style="flex: 1;">-</td>`;
        if (datapoint.drecovered != 0) { 
            dr = `<td class="mx-1" style="flex: 1;">${datapoint.drecovered} (${rp}%)</td>`;
        }

        let d = `<td class="mx-1" style="flex: 1;">-</td>`;
        if (datapoint.deaths != 0) { 
            d = `<td class="mx-1" style="flex: 1;">${datapoint.deaths}</td>`;
        }

        let dd = `<td class="mx-1" style="flex: 1;">-</td>`;
        if (datapoint.ddeaths != 0) { 
            dd = `<td class="mx-1" style="flex: 1;">${datapoint.ddeaths} (${dp}%)</td>`;
        }

        let num_tests = `<td class="mx-1" style="flex: 1;">-</td>`;
        if (datapoint.num_tests) {
            dd = `<td class="mx-1" style="flex: 1;">${datapoint.num_tests}</td>`;
        }

        $("#tablebody")[0].innerHTML += `
        <tr class="datatable-row" data-label="${label}">
            <td class="mx-1" style="flex: 2;">${label}</td>
            <td class="mx-1" style="flex: 1;">${datapoint.confirmed}</td>
            ${dc}
            ${r}
            ${dr}
            ${d}
            ${dd}
            ${num_tests}
        </tr>
        `;

        i += 1;
    }

}

function set_country(country) {
    $("#country-selector").val(country);
    $("#country-selector").trigger("change");
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

    $.getJSON(
        "/cases/totals",
        params,
        function(result) {
            by_country[entry_date] = result;
            show_data(result, level, def);
        }
    );
}
