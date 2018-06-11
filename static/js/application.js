undo_rgb = null;
rgb_values = [0, 0, 0];
hsl_values = [0, 0, 0];
relative_brightness = 0;

$(document).ready(function() {
    $('input#led-red, input#led-green, input#led-blue').change(function() {
        on_rgb_sliders_changed(true);
    });
    $('a#led-undo').click(function() {
        $.post('/led', {rgb: undo_rgb}, function() {
            undo_rgb = null;
            update_led_sliders_from_server();
        })
    });
    $('a#led-on').click(function() {
        $.post('/led', {rgb: '255,255,255'}, function() {
            undo_rgb = get_led_sliders_rgb();
            update_led_sliders_from_server();
        })
    });
    $('a#led-off').click(function() {
        $.post('/led', {rgb: '0,0,0'}, function() {
            undo_rgb = get_led_sliders_rgb();
            update_led_sliders_from_server();
        })
    });
    $('a#led-darker-btn').click(function() {
        change_brightness(-1);
    });
    $('a#led-brighter-btn').click(function() {
        change_brightness(1);
    });

    update_led_sliders_from_server();
});

function get_led_sliders_rgb() {
    return $('input#led-red').val() + ',' + $('input#led-green').val() + ',' + $('input#led-blue').val();
}

function update_led_sliders_from_server() {
    $.get('/led', function(data) {
        rgb_values = data['rgb'].split(',');
        relative_brightness = 0;
        hsl_values = data['hsl'].split(',');

        $('input#led-red').val(rgb_values[0]);
        $('input#led-green').val(rgb_values[1]);
        $('input#led-blue').val(rgb_values[2]);

        $('input#led-hue').val(hsl_values[0]);
        $('input#led-saturation').val(hsl_values[1]);
        $('input#led-lightness').val(hsl_values[2]);

        update_led_buttons_visibility();
    });
}

function on_rgb_sliders_changed(is_user_input) {
    undo_rgb = null;
    if (is_user_input) {
        rgb_values = [
            $('input#led-red').val(),
            $('input#led-green').val(),
            $('input#led-blue').val()
        ];

        relative_brightness = 0;
    }

    $.post('/led', {rgb: get_led_sliders_rgb()});
    update_led_buttons_visibility();
}

function change_brightness(delta) {
    var BRIGHTNESS_QUOTIENT = 1.25;
    var CHANNEL_MAX = 255;

    relative_brightness += delta;

    var corrected_rgb_values = rgb_values.slice();
    for (i in corrected_rgb_values) {
        if (corrected_rgb_values[i] == 0) {
            corrected_rgb_values[i] = 0.5;
        }
        corrected_rgb_values[i] = Math.round(Math.pow(BRIGHTNESS_QUOTIENT, relative_brightness) * corrected_rgb_values[i]);
        if (corrected_rgb_values[i] > CHANNEL_MAX) {
            corrected_rgb_values[i] = CHANNEL_MAX;
        }
    }

    $('input#led-red').val(corrected_rgb_values[0]);
    $('input#led-green').val(corrected_rgb_values[1]);
    $('input#led-blue').val(corrected_rgb_values[2]);

    on_rgb_sliders_changed(false);
}

function update_led_buttons_visibility() {
    rgb = get_led_sliders_rgb();
    undo_display = (undo_rgb != null);
    on_display = (rgb != '255,255,255');
    off_display = (rgb != '0,0,0');
    $('a#led-undo').css('display', undo_display ? 'inline' : 'none');
    $('a#led-on').css('display', on_display ? 'inline' : 'none');
    $('a#led-off').css('display', off_display ? 'inline' : 'none');
}