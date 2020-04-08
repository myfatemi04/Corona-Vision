let country_list = [];
let province_list = {};
let admin2_list = {};

let province_head = '<option value="">Whole country</option>';
let country_head = '<option value="">Whole world</option>';
let admin2_head = '<option value="">Whole state</option>';

function generate_name(country, province, admin2) {
    let l = '';
    if (admin2) {
        l += admin2 + ", ";
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

function init_selectors() {
    $.getJSON(
        "/list/countries",
        {
            date: $("#date")[0].value,
            need_province: CORONA_GLOBALS.need_child
        },
        function(data) {
            add_selector_items("country-selector", country_head, data);
            country_list = data;
        }
    )

    $("#country-selector").change(
        function() {
            CORONA_GLOBALS.country = this.value;
            CORONA_GLOBALS.province = "";
            CORONA_GLOBALS.admin2 = "";
            
            CORONA_GLOBALS.reload_function();

            $("#province-selector").hide();
            $("#province-selector")[0].innerHTML = province_head;
            $("#admin2-selector").hide();
            $("#admin2-selector")[0].innerHTML = admin2_head;
                
            if (this.value) {
                let country = CORONA_GLOBALS.country;

                if (!province_list.hasOwnProperty(country)) {
                    $.getJSON(
                        "/list/provinces",
                        {
                            country: country,
                            date: $("#date")[0].value,
                            need_admin2: CORONA_GLOBALS.need_child
                        },
                        function(data) {
                            province_list[country] = data;
                            add_selector_items("province-selector", province_head, province_list[country]);
                        }
                    )
                } else {
                    add_selector_items("province-selector", province_head, province_list[country]);
                }
            }
        }
    );

    $("#province-selector").change(
        function() {
            CORONA_GLOBALS.province = this.value;
            CORONA_GLOBALS.admin2 = "";
            
            CORONA_GLOBALS.reload_function();
            
            $("#admin2-selector").hide();
            $("#admin2-selector")[0].innerHTML = admin2_head;
            
            if (this.value) {    
                let country = CORONA_GLOBALS.country;
                let province = CORONA_GLOBALS.province;
                let admin2 = CORONA_GLOBALS.admin2;

                if (!admin2_list.hasOwnProperty(country)) {
                    admin2_list[country] = {};
                }

                if (!admin2_list[country].hasOwnProperty(province)) {
                    $.getJSON(
                        "/list/admin2",
                        { country: country, province: province },
                        function(data) {
                            admin2_list[country][province] = data;
                            add_selector_items("admin2-selector", admin2_head, admin2_list[country][province]);
                        }
                    );
                } else {
                    add_selector_items("admin2-selector", admin2_head, admin2_list[country][province]);
                }
            }
        }
    );

    $("#admin2-selector").change(
        function() {
            CORONA_GLOBALS.admin2 = $("#admin2-selector")[0].value;
            
            CORONA_GLOBALS.reload_function();
        }
    );
}