$(document).ready(function() {
    $('input#red, input#green, input#blue').change(function() {
        update_ledcolor();
    });
});

function update_ledcolor() {
    rgb = $('input#red').val() + ',' + $('input#green').val() + ',' + $('input#blue').val();
    $.post('/led', {rgb: rgb});
}