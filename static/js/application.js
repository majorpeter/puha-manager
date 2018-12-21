undo_rgb = null;
rgb_values = [0, 0, 0];
hsl_values = [0, 0, 0];
relative_brightness = 0;

$(document).ready(function() {
    $('input#led-red, input#led-green, input#led-blue').on('input', function() {
        on_rgb_sliders_changed(true, false);
    });
    $('input#led-hue, input#led-saturation, input#led-lightness').on('input', function() {
        on_hsl_sliders_changed();
    });
    $('a#led-undo').click(function() {
        $.post('/led', {rgb: undo_rgb, animate: 1.0}, function() {
            undo_rgb = null;
            setTimeout(update_led_sliders_from_server, 100);
        })
    });
    $('a#led-on').click(function() {
        $.post('/led', {rgb: '255,255,255', animate: 1.0}, function() {
            undo_rgb = get_led_sliders_rgb();
            setTimeout(update_led_sliders_from_server, 100);
        })
    });
    $('a#led-off').click(function() {
        $.post('/led', {rgb: '0,0,0', animate: 1.0}, function() {
            undo_rgb = get_led_sliders_rgb();
            setTimeout(update_led_sliders_from_server, 100);
        })
    });
    $('a#led-darker-btn').click(function() {
        change_brightness(-1);
    });
    $('a#led-brighter-btn').click(function() {
        change_brightness(1);
    });

    $('input[name="led-control-mode"]').change(function() {
        $.post('/lightcontrol', {
            mode: this.value
        });
        update_kept_illuminance_visiblity_and_value_from_server();
        update_animation_select_visibility_and_value_from_server();
    });

    $('input#kept-illuminance').on('input', function() {
        if ($('input[name="led-control-mode"]:checked').val() == 'KeepIlluminance') {
                $.post('/lightcontrol', {
                    mode: 'KeepIlluminance',
                    illuminance: this.value
                });
        }
    });

    $('div#led-tabs a').click(function(e) {
        var tab = this.getAttribute('href');
        localStorage.setItem('activeLedTab', tab);
        if (tab != '#led-tune-control') {
            update_led_sliders_from_server();
        } else {
            update_light_control_from_server();
        }
    });

    update_led_sliders_from_server();
    update_light_control_from_server();
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

function update_light_control_from_server() {
    $.get('/lightcontrol', function(data) {
        $('input[name="led-control-mode"][value="' + data['mode'].split('.')[1] + '"]').prop('checked', true);
        update_kept_illuminance_visiblity_and_value_from_server();
        update_animation_select_visibility_and_value_from_server();
    });
}

function update_kept_illuminance_visiblity_and_value_from_server() {
    if ($('input[name="led-control-mode"]:checked').val() == 'KeepIlluminance') {
        $.get('/lightsensor', function(data) {
            $('input#kept-illuminance').val(data['illuminance']);
            $('input#kept-illuminance').removeClass('hide');
        });
    } else {
        $('input#kept-illuminance').addClass('hide');
    }
}

function update_animation_select_visibility_and_value_from_server() {
    if ($('input[name="led-control-mode"]:checked').val() == 'Animate') {
        $('div#animation-select').removeClass('hide');
    } else {
        $('div#animation-select').addClass('hide');
    }
}

function on_rgb_sliders_changed(is_user_input, animate) {
    undo_rgb = null;
    if (is_user_input) {
        rgb_values = [
            $('input#led-red').val(),
            $('input#led-green').val(),
            $('input#led-blue').val()
        ];

        relative_brightness = 0;
    }

    data = {rgb: get_led_sliders_rgb()}
    if (animate) {
        data['animate'] = animate
    }
    $.post('/led', data);
    update_led_buttons_visibility();
}

function on_hsl_sliders_changed() {
    undo_rgb = null;
    rgb_values = null;
    relative_brightness = 0;
    $.post('/led', {
        hsl: $('input#led-hue').val() + ', ' + $('input#led-saturation').val() + ', ' + $('input#led-lightness').val()
    });
    //TODO update_led_buttons_visibility();
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

    on_rgb_sliders_changed(false, 0.3);
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