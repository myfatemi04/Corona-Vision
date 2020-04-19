CORONA_GLOBALS.admin0_list = [];
CORONA_GLOBALS.admin1_list = {};
CORONA_GLOBALS.admin2_list = {};

let admin1_head = '<option value="">Whole country</option>';
let admin0_head = '<option value="">Whole world</option>';
let admin2_head = '<option value="">Whole state</option>';

function generate_name(admin0, admin1, admin2) {
    let l = '';
    if (admin2) {
        l += admin2 + ", ";
    }
    if (admin1) {
        l += admin1 + ", ";
    }
    if (admin0) {
        l += admin0;
    }
    if (!l) {
        return "World";
    }
    return l;
}

function add_selector_items(id, head, admin0_list) {
    let elem_pointer = $("#" + id);
    let elem = elem_pointer[0];
    if (admin0_list.length > 0) {
        elem_pointer.show();
    }
    elem.innerHTML = head;
    for (let admin0 of admin0_list) {
        elem.innerHTML += `<option value="${admin0}">${admin0}</option>`;
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
            CORONA_GLOBALS.admin0_list = data.map(({admin0}) => admin0);
            add_selector_items("admin0-selector", admin0_head, CORONA_GLOBALS.admin0_list);
        }
    )

    $("#admin0-selector").change(
        function() {
            CORONA_GLOBALS.admin0 = this.value;
            CORONA_GLOBALS.admin1 = "";
            CORONA_GLOBALS.admin2 = "";
            
            $("#admin1-selector").hide();
            $("#admin1-selector")[0].innerHTML = admin1_head;
            $("#admin2-selector").hide();
            $("#admin2-selector")[0].innerHTML = admin2_head;
                
            if (this.value) {
                let admin0 = CORONA_GLOBALS.admin0;

                if (!CORONA_GLOBALS.admin1_list.hasOwnProperty(admin0)) {
                    $.getJSON(
                        "/list/admin1s",
                        {
                            admin0: admin0,
                            date: $("#date")[0].value,
                            need_admin2: need_child
                        },
                        function(data) {
                            CORONA_GLOBALS.admin1_list[admin0] = data.map(({admin1}) => admin1);
                            add_selector_items("admin1-selector", admin1_head, CORONA_GLOBALS.admin1_list[admin0]);
                            after_change();
                        }
                    )
                } else {
                    add_selector_items("admin1-selector", admin1_head, CORONA_GLOBALS.admin1_list[admin0]);
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
            CORONA_GLOBALS.admin2 = "";
            
            $("#admin2-selector").hide();
            $("#admin2-selector")[0].innerHTML = admin2_head;
            
            if (this.value) {    
                let admin0 = CORONA_GLOBALS.admin0;
                let admin1 = CORONA_GLOBALS.admin1;

                if (!CORONA_GLOBALS.admin2_list.hasOwnProperty(admin0)) {
                    CORONA_GLOBALS.admin2_list[admin0] = {};
                }

                if (!CORONA_GLOBALS.admin2_list[admin0].hasOwnProperty(admin1)) {
                    $.getJSON(
                        "/list/admin2",
                        { admin0: admin0, admin1: admin1, date: $("#date")[0].value },
                        function(data) {
                            CORONA_GLOBALS.admin2_list[admin0][admin1] = data.map(({admin2}) => admin2);
                            add_selector_items("admin2-selector", admin2_head, CORONA_GLOBALS.admin2_list[admin0][admin1]);
                            after_change();
                        }
                    );
                } else {
                    add_selector_items("admin2-selector", admin2_head, CORONA_GLOBALS.admin2_list[admin0][admin1]);
                    after_change();
                }
            } else {
                after_change();
            }
        }
    );

    $("#admin2-selector").change(
        function() {
            CORONA_GLOBALS.admin2 = $("#admin2-selector")[0].value;
            after_change();
        }
    );
}