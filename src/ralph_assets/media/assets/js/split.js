$(document).ready(function () {
    var FORM_COUNT = parseInt($('input[name="form-TOTAL_FORMS"]').val());

    $('.add_row').on("click", function () {
        var row_html = $('#row-to-copy').html();
        $('.form-split tbody').append(row_html)
        change_form_counter('add');
        renumber_forms();
        bas = BobAjaxSelect.getInstance();
        bas.register_in_element($('.form-split tbody tr').last());
        return false;
    });

    $("body").delegate(".form-split .delete_row", "click", function () {
        var row_count = $('.form-split tbody tr').length;
        if (row_count > 1) {
            $(this).parents('tr').remove();
        }
        change_form_counter('subtract');
        renumber_forms();
        return false;
    });

    function change_form_counter(action) {
        if (action == 'add') {
            FORM_COUNT += 1;
        } else if (action == 'subtract') {
            FORM_COUNT -= 1;
        }
        $('input[name="form-TOTAL_FORMS"]').val(FORM_COUNT);
    }

    function renumber_forms() {
        var form = $('.form-split tr');
        form.each(function (i, elem) {
            $(elem).find('input, select, span, div,').each(function (j, elem) {
                var numberPattern = /\d+/g;
                var name = $(elem).attr('name');
                if (name) {
                    $(elem).attr('name', name.replace(numberPattern, i - 1));
                }
                var id = $(elem).attr('id');
                if (id) {
                    $(elem).attr('id', id.replace(numberPattern, i - 1));
                }
            });

        });

        $('.ordinal').each(function (i, elem) {
            $(elem).html(i + 1);
        });
    }
});
