undo_rgb = null;

$(document).ready(function() {
    $('input#led-red, input#led-green, input#led-blue').change(function() {
        update_ledcolor();
    });
    $('a#led-undo').click(function() {
        $.post('/led', {rgb: undo_rgb}, function() {
            undo_rgb = null;
            refresh_ledcolor();
        })
    });
    $('a#led-on').click(function() {
        $.post('/led', {rgb: '255,255,255'}, function() {
            undo_rgb = get_led_sliders_rgb();
            refresh_ledcolor();
        })
    });
    $('a#led-off').click(function() {
        $.post('/led', {rgb: '0,0,0'}, function() {
            undo_rgb = get_led_sliders_rgb();
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
    undo_rgb = null;
    $.post('/led', {rgb: get_led_sliders_rgb()});
    refresh_ledbuttons();
}

function refresh_ledbuttons() {
    rgb = get_led_sliders_rgb();
    undo_display = (undo_rgb != null);
    on_display = (rgb != '255,255,255');
    off_display = (rgb != '0,0,0');
    $('a#led-undo').css('display', undo_display ? 'inline' : 'none');
    $('a#led-on').css('display', on_display ? 'inline' : 'none');
    $('a#led-off').css('display', off_display ? 'inline' : 'none');
}