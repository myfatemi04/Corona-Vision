function update_chart_location() {
    let country = $("#country-selector")[0].value;
    let province = $("#province-selector")[0].value;
    let admin2 = $("#admin2-selector")[0].value;
    
    let label = generate_name(country, province, admin2);
    
    show_chart(country, province, admin2, label, main_chart);
}
function init_chart_options(chart) {
    $("select[name=scale-type]").change(
        function() {
            if (this.value == 'logarithmic' || this.value == 'linear') {
                chart.options.scales.yAxes[0].type = this.value;
                chart.update();
            }
        }
    );

    $("select[name=chart-type]").change(
        function() {
            chart_type = this.value;
            update_chart_location();
        }
    );

    $("input[name=display-confirmed]").change(
        function() {
            chart.data.datasets[CONFIRMED_IX].hidden = !this.checked;
            chart.update();
        }
    );

    $("input[name=display-deaths]").change(
        function() {
            chart.data.datasets[DEATHS_IX].hidden = !this.checked;
            chart.update();
        }
    );

    $("input[name=display-recovered]").change(
        function() {
            chart.data.datasets[RECOVERED_IX].hidden = !this.checked;
            chart.update();
        }
    );

    $("input[name=display-active]").change(
        function() {
            chart.data.datasets[ACTIVE_IX].hidden = !this.checked;
            chart.update();
        }
    );
}