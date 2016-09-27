
/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

jQuery(function ($) {

    /********
        Toggling of New Office / Office Name / Office Category
    ********/

    function setOffice() {
        var select_widget = $("#form-widgets-office"),
            index = parseInt($("#form-widgets-office").val()),
            option = select_widget.find('option').eq(index).html(),
            office_name_control = $("#form-widgets-office_name"),
            office_category_control = $("#form-widgets-office_category"),
            office_name_field = $("#formfield-form-widgets-office_name"),
            office_category_field = $("#formfield-form-widgets-office_category"),
            office_name,
            office_category,
            osplit;

        if (option === 'New Office') {
            office_name_control.val('');
            office_category_control.val('');
            office_name_field.slideDown();
            office_category_field.slideDown();
        } else {
            osplit = option.split(/ *\| */);
            if (osplit.length === 2) {
                office_name_control.val(osplit[1]);
                office_category_control.val(osplit[0]);
                office_name_field.slideUp();
                office_category_field.slideUp();
            }
        }
    }

    if ($("body.template-candidate_filing").length) {
        setOffice();
        $("#form-widgets-office").change(function () {
            setOffice();
        });
    }

});