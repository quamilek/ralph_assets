$(document).ready(function () {
    var FORM_COUNT = parseInt($('input[name="form-TOTAL_FORMS"]').val());

    $('.add_row').on("click", function () {
        var ajax_fetch_url = $(this).data('ajax-fetch-url');
        if (ajax_fetch_url){

            var row =
            $.get(ajax_fetch_url + '?replace_id=' + FORM_COUNT, function(template) {
                    $(".form-split tbody").append(template);
            });
        } else {
            var row = $('.form-split tbody tr').last().clone(true, true);
            cleanup_fields(row);
            row.appendTo(".form-split tbody");
        }
        change_form_counter('add');
        // renumber_forms();
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

    $(".input, .uneditable-input").on("click", function () {
        $(this).parent().next("td").find('input').val($(this).html());
    });

    function change_form_counter(action) {
        if (action == 'add') {
            FORM_COUNT += 1;
        } else if (action == 'subtract') {
            FORM_COUNT -= 1;
        }
        $('input[name="form-TOTAL_FORMS"]').val(FORM_COUNT);
    }

    function cleanup_fields(row) {
        row.find('input, select').each(function (i, elem) {
            $(elem).val('');
            td_class = $(elem).parent().attr('class');
            td_class = td_class.replace('error', '');
            $(elem).parent().attr('class', td_class);
        });
        row.find('.help-inline').remove();
        row.find('.uneditable-input').html('');
        return false;
    }

    function renumber_forms() {
        var form = $('.form-split tr');
        form.each(function (i, elem) {
            $(elem).find('input, select').each(function (j, elem) {
                var numberPattern = /\d+/g;
                var name = $(elem).attr('name');
                $(elem).attr('name', name.replace(numberPattern, i - 1));
                var id = $(elem).attr('id');
                $(elem).attr('id', name.replace(numberPattern, i - 1));
            });

        });
        $('.ordinal').each(function (i, elem) {
            $(elem).html(i + 1);
        });
    }
});
