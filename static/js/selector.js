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

function add_selector_items(elem, head, country_list) {
    elem.innerHTML = head;
    for (let country of country_list) {
        elem.innerHTML += `<option value="${country}">${country}</option>`;
    }
}

function init_selectors() {

    $.getJSON(
        "/list/countries",
        {},
        function(data) {
            add_selector_items($("#country-selector")[0], country_head, data);
            country_list = data;
        }
    )

    $("#country-selector").change(
        function() {
            CHART_OPTIONS.country = this.value;
            CHART_OPTIONS.province = "";
            CHART_OPTIONS.admin2 = "";
            
            CHART_OPTIONS.reload_function();

            if (!this.value) {
                $("#province-selector")[0].disabled = true;
                $("#province-selector")[0].innerHTML = province_head;
                $("#admin2-selector")[0].disabled = true;
                $("#admin2-selector")[0].innerHTML = admin2_head;
            } else {
                $("#province-selector")[0].disabled = false;
                $("#admin2-selector")[0].disabled = true;
                $("#admin2-selector")[0].innerHTML = admin2_head;
                
                let country = CHART_OPTIONS.country;

                if (!province_list.hasOwnProperty(country)) {
                    $.getJSON(
                        "/list/provinces",
                        { country: country },
                        function(data) {
                            province_list[country] = data;
                            add_selector_items($("#province-selector")[0], province_head, province_list[country]);
                        }
                    )
                } else {
                    add_selector_items($("#province-selector")[0], province_head, province_list[country]);
                }
            }
        }
    );

    $("#province-selector").change(
        function() {
            CHART_OPTIONS.province = this.value;
            CHART_OPTIONS.admin2 = "";
            
            CHART_OPTIONS.reload_function();

            if (!this.value) {
                $("#admin2-selector")[0].disabled = true;
                $("#admin2-selector")[0].innerHTML = admin2_head;
            } else {
                $("#admin2-selector")[0].disabled = false;
                
                let country = CHART_OPTIONS.country;
                let province = CHART_OPTIONS.province;
                let admin2 = CHART_OPTIONS.admin2;

                if (!admin2_list.hasOwnProperty(country)) {
                    admin2_list[country] = {};
                }

                if (!admin2_list[country].hasOwnProperty(province)) {
                    $.getJSON(
                        "/list/admin2",
                        { country: country, province: province },
                        function(data) {
                            admin2_list[country][province] = data;
                            add_selector_items($("#admin2-selector")[0], admin2_head, admin2_list[country][province]);
                        }
                    );
                } else {
                    add_selector_items($("#admin2-selector")[0], admin2_head, admin2_list[country][province]);
                }
            }
        }
    );

    $("#admin2-selector").change(
        function() {
            CHART_OPTIONS.admin2 = $("#admin2-selector")[0].value;
            
            CHART_OPTIONS.reload_function();
        }
    );
}