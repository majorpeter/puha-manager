$(document).ready(function() {
    $('input#led-red, input#led-green, input#led-blue').change(function() {
        update_ledcolor();
    });
    $('a#led-on').click(function() {
        $.post('/led', {rgb: '255,255,255'}, function() {
            refresh_ledcolor();
        })
    });
    $('a#led-off').click(function() {
        $.post('/led', {rgb: '0,0,0'}, function() {
            refresh_ledcolor();
        })
    });

    refresh_ledcolor();
});

function get_led_sliders_rgb() {
    return $('input#led-red').val() + ',' + $('input#led-green').val() + ',' + $('input#led-blue').val();
}

function refresh_ledcolor() {
    $.get('/led', function(data) {
        rgb = data['rgb'].split(',');
        $('input#led-red').val(rgb[0]);
        $('input#led-green').val(rgb[1]);
        $('input#led-blue').val(rgb[2]);
        refresh_ledbuttons();
    });
}

function update_ledcolor() {
    $.post('/led', {rgb: get_led_sliders_rgb()});
    refresh_ledbuttons();
}

function refresh_ledbuttons() {
    rgb = get_led_sliders_rgb();
    on_display = (rgb != '255,255,255');
    off_display = (rgb != '0,0,0');
    $('a#led-on').css('display', on_display ? 'inline' : 'none');
    $('a#led-off').css('display', off_display ? 'inline' : 'none');
}