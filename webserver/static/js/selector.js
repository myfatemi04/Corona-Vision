CORONA_GLOBALS.country_list = [];
CORONA_GLOBALS.province_list = {};
CORONA_GLOBALS.county_list = {};

let province_head = '<option value="">Whole country</option>';
let country_head = '<option value="">Whole world</option>';
let county_head = '<option value="">Whole state</option>';

function generate_name(country, province, county) {
    let l = '';
    if (county) {
        l += county + ", ";
    }
    if (province) {
        l += province + ", ";
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
            need_province: need_child
        },
        function(data) {
            CORONA_GLOBALS.country_list = data.map(({country}) => country);
            add_selector_items("country-selector", country_head, CORONA_GLOBALS.country_list);
        }
    )

    $("#country-selector").change(
        function() {
            CORONA_GLOBALS.country = this.value;
            CORONA_GLOBALS.province = "";
            CORONA_GLOBALS.county = "";
            
            $("#province-selector").hide();
            $("#province-selector")[0].innerHTML = province_head;
            $("#county-selector").hide();
            $("#county-selector")[0].innerHTML = county_head;
                
            if (this.value) {
                let country = CORONA_GLOBALS.country;

                if (!CORONA_GLOBALS.province_list.hasOwnProperty(country)) {
                    $.getJSON(
                        "/list/provinces",
                        {
                            country: country,
                            date: $("#date")[0].value,
                            need_county: need_child
                        },
                        function(data) {
                            CORONA_GLOBALS.province_list[country] = data.map(({province}) => province);
                            add_selector_items("province-selector", province_head, CORONA_GLOBALS.province_list[country]);
                            after_change();
                        }
                    )
                } else {
                    add_selector_items("province-selector", province_head, CORONA_GLOBALS.province_list[country]);
                    after_change();
                }
            } else {
                after_change();
            }
        }
    );

    $("#province-selector").change(
        function() {
            CORONA_GLOBALS.province = this.value;
            CORONA_GLOBALS.county = "";
            
            $("#county-selector").hide();
            $("#county-selector")[0].innerHTML = county_head;
            
            if (this.value) {    
                let country = CORONA_GLOBALS.country;
                let province = CORONA_GLOBALS.province;

                if (!CORONA_GLOBALS.county_list.hasOwnProperty(country)) {
                    CORONA_GLOBALS.county_list[country] = {};
                }

                if (!CORONA_GLOBALS.county_list[country].hasOwnProperty(province)) {
                    $.getJSON(
                        "/list/county",
                        { country: country, province: province, date: $("#date")[0].value },
                        function(data) {
                            CORONA_GLOBALS.county_list[country][province] = data.map(({county}) => county);
                            add_selector_items("county-selector", county_head, CORONA_GLOBALS.county_list[country][province]);
                            after_change();
                        }
                    );
                } else {
                    add_selector_items("county-selector", county_head, CORONA_GLOBALS.county_list[country][province]);
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