$(document).ready(function() {
    "use strict";
    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            "url": Flask.url_for('examination.get_courses'),
            "type": "get"
        }
    }, utils.datatables.defaults));

    $('#datatable').on('click', 'tr', function () {
        window.location.href = Flask.url_for('examination.edit_course', {
            course_id: table.row(this).data()[0]}) + '?redir=courses';
    });
});
