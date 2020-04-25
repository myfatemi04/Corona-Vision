/* recursive function to animate */
function animate() {
    if (!do_animation) return;
    let select = $("select[name=map-date]")[0];
    if (select.selectedIndex > 0) {
        select.selectedIndex--;
        setTimeout(
            () => {
                setDate($("#date").val(), animate)
            },
            1000/fps
        );
    } else {
        do_animation = false;
    }
}

function stop_animation() {
    do_animation = false;
}

function start_animation() {
    if (!do_animation) {
        do_animation = true;
        set_start_date();
        animate();
    }
}

function animate_now() {
    if (!do_animation) {
        do_animation = true;
        animate();
    }
}

let do_animation = false;
let fps = 4;

function set_start_date() {
    let select = $("select[name=map-date]")[0];
    select.selectedIndex = select.options.length-1;
}

function setFps(value) {
    fps = value;
}