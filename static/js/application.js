$(document).ready(function() {
    $('input#red, input#green, input#blue').change(function() {
        update_ledcolor();
    });

    init_ledcolor();
});

function init_ledcolor() {
    $.get('/led', function(data) {
        rgb = data['rgb'].split(',');
        $('input#red').val(rgb[0]);
        $('input#green').val(rgb[1]);
        $('input#blue').val(rgb[2]);
    });
}

function update_ledcolor() {
    rgb = $('input#red').val() + ',' + $('input#green').val() + ',' + $('input#blue').val();
    $.post('/led', {rgb: rgb});
}