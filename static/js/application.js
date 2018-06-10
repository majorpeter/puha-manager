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

function refresh_ledcolor() {
    $.get('/led', function(data) {
        rgb = data['rgb'].split(',');
        $('input#led-red').val(rgb[0]);
        $('input#led-green').val(rgb[1]);
        $('input#led-blue').val(rgb[2]);
    });
}

function update_ledcolor() {
    rgb = $('input#led-red').val() + ',' + $('input#led-green').val() + ',' + $('input#led-blue').val();
    $.post('/led', {rgb: rgb});
}