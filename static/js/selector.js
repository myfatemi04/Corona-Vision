let country_list = [];
let province_list = {};
let admin2_list = {};

let country = '';
let province = '';
let admin2 = '';

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

function add_list(elem, head, country_list) {
    elem.innerHTML = head;
    for (let country of country_list) {
        elem.innerHTML += `<option value="${country}">${country}</option>`;
    }
}

function init_selectors(update_func) {
    $.getJSON(
        "/list/countries",
        {},
        function(data) {
            add_list($("#country-selector")[0], country_head, data);
            country_list = data;
        }
    )

    $("#country-selector").change(
        function() {
            country = this.value;
            province = "";
            admin2 = "";
            
            update_func();

            if (!this.value) {
                $("#province-selector")[0].disabled = true;
                $("#province-selector")[0].innerHTML = province_head;
                $("#admin2-selector")[0].disabled = true;
                $("#admin2-selector")[0].innerHTML = admin2_head;
            } else {
                $("#province-selector")[0].disabled = false;
                $("#admin2-selector")[0].disabled = true;
                $("#admin2-selector")[0].innerHTML = admin2_head;
                

                if (!province_list.hasOwnProperty(country)) {
                    $.getJSON(
                        "/list/provinces",
                        { country: country },
                        function(data) {
                            province_list[country] = data;
                            add_list($("#province-selector")[0], province_head, province_list[country]);
                        }
                    )
                } else {
                    add_list($("#province-selector")[0], province_head, province_list[country]);
                }
            }
        }
    );

    $("#province-selector").change(
        function() {
            province = this.value;
            admin2 = "";

            update_func();

            if (!this.value) {
                $("#admin2-selector")[0].disabled = true;
                $("#admin2-selector")[0].innerHTML = admin2_head;
            } else {
                $("#admin2-selector")[0].disabled = false;

                if (!admin2_list.hasOwnProperty(country)) {
                    admin2_list[country] = {};
                }

                if (!admin2_list[country].hasOwnProperty(province)) {
                    $.getJSON(
                        "/list/admin2",
                        { country: country, province: province },
                        function(data) {
                            admin2_list[country][province] = data;
                            add_list($("#admin2-selector")[0], admin2_head, admin2_list[country][province]);
                        }
                    );
                } else {
                    add_list($("#admin2-selector")[0], admin2_head, admin2_list[country][province]);
                }
            }
        }
    );

    $("#admin2-selector").change(
        function() {
            admin2 = $("#admin2-selector")[0].value;
            update_func();
        }
    );
}