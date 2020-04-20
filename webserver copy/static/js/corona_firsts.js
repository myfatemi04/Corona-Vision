function load_data() {
    $.getJSON(
        "/cases/first_days",
        {},
        function(data) {
            add_data(data);
        }
    )
}

function add_data(data) {
    let tbody = $("#table-body")[0];
    let last_loc_cell = null;
    let last_entry_date = null;
    for (let result of data) {
        if (result.admin2 == '' && result.admin1 == '' && result.admin0 != '') {
            let new_row = tbody.insertRow(-1);
            if (last_entry_date && last_entry_date == result.entry_date) {
                last_loc_cell.innerHTML += "<br/>" + result.admin0;
            } else {
                let date_cell = new_row.insertCell(-1);
                let location_cell = new_row.insertCell(-1);
                date_cell.innerHTML = result.entry_date;
                location_cell.innerHTML = result.admin0;
                last_loc_cell = location_cell;
                last_entry_date = result.entry_date;
            }
        }
    }
}