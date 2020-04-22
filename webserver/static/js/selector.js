CORONA_GLOBALS.country_list = [];
CORONA_GLOBALS.admin1_list = {};
CORONA_GLOBALS.county_list = {};

let admin1_head = '<option value="">Whole country</option>';
let country_head = '<option value="">Whole world</option>';
let county_head = '<option value="">Whole state</option>';

function generate_name(country, admin1, county) {
    let l = '';
    if (county) {
        l += county + ", ";
    }
    if (admin1) {
        l += admin1 + ", ";
    }
    if (country) {
        l += country;
    }
    if (!l) {
        return "World";
    }
    return l;
}

function add_selector_items(id, head, country_list) {
    let elem_pointer = $("#" + id);
    let elem = elem_pointer[0];
    if (country_list.length > 0) {
        elem_pointer.show();
    }
    elem.innerHTML = head;
    for (let country of country_list) {
        elem.innerHTML += `<option value="${country}">${country}</option>`;
    }
}

function init_selectors(after_change, need_child) {
    $.getJSON(
        "/list/countries",
        {
            date: $("#date")[0].value,
            need_admin1: need_child
        },
        function(data) {
            CORONA_GLOBALS.country_list = data.map(({country}) => country);
            add_selector_items("country-selector", country_head, CORONA_GLOBALS.country_list);
        }
    )

    $("#country-selector").change(
        function() {
            CORONA_GLOBALS.country = this.value;
            CORONA_GLOBALS.admin1 = "";
            CORONA_GLOBALS.county = "";
            
            $("#admin1-selector").hide();
            $("#admin1-selector")[0].innerHTML = admin1_head;
            $("#county-selector").hide();
            $("#county-selector")[0].innerHTML = county_head;
                
            if (this.value) {
                let country = CORONA_GLOBALS.country;

                if (!CORONA_GLOBALS.admin1_list.hasOwnProperty(country)) {
                    $.getJSON(
                        "/list/provinces",
                        {
                            country: country,
                            date: $("#date")[0].value,
                            need_county: need_child
                        },
                        function(data) {
                            CORONA_GLOBALS.admin1_list[country] = data.map(({admin1}) => admin1);
                            add_selector_items("admin1-selector", admin1_head, CORONA_GLOBALS.admin1_list[country]);
                            after_change();
                        }
                    )
                } else {
                    add_selector_items("admin1-selector", admin1_head, CORONA_GLOBALS.admin1_list[country]);
                    after_change();
                }
            } else {
                after_change();
            }
        }
    );

    $("#admin1-selector").change(
        function() {
            CORONA_GLOBALS.admin1 = this.value;
            CORONA_GLOBALS.county = "";
            
            $("#county-selector").hide();
            $("#county-selector")[0].innerHTML = county_head;
            
            if (this.value) {    
                let country = CORONA_GLOBALS.country;
                let admin1 = CORONA_GLOBALS.admin1;

                if (!CORONA_GLOBALS.county_list.hasOwnProperty(country)) {
                    CORONA_GLOBALS.county_list[country] = {};
                }

                if (!CORONA_GLOBALS.county_list[country].hasOwnProperty(admin1)) {
                    $.getJSON(
                        "/list/county",
                        { country: country, admin1: admin1, date: $("#date")[0].value },
                        function(data) {
                            CORONA_GLOBALS.county_list[country][admin1] = data.map(({county}) => county);
                            add_selector_items("county-selector", county_head, CORONA_GLOBALS.county_list[country][admin1]);
                            after_change();
                        }
                    );
                } else {
                    add_selector_items("county-selector", county_head, CORONA_GLOBALS.county_list[country][admin1]);
                    after_change();
                }
            } else {
                after_change();
            }
        }
    );

    $("#county-selector").change(
        function() {
            CORONA_GLOBALS.county = $("#county-selector")[0].value;
            after_change();
        }
    );
}