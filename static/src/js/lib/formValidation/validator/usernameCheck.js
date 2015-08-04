/**
 * usernameCheck validator
 */

(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("validator/usernameCheck", ["jquery", "base", "csrf"], factory);
    } else {
        // planted over the root!
        factory(root.jQuery, root.FormValidation);
    }

}(this, function ($, FormValidation, csrfHeader) {
    FormValidation.I18n = $.extend(true, FormValidation.I18n || {}, {
        'en_US': {
            usernameCheck: {
                'default': 'Please input the same value'
            }
        }
    });

    FormValidation.Validator.usernameCheck = {

        validate: function(validator, $field, options) {
                    if ($field.val() == '')
                        return true;
                    return !$.ajax({
                    async: false,
                    beforeSend: csrfHeader,
                    url: "/api/username_check/",
                    data: {username: $field.val()},
                    dataType: "json",
                    method: "post",


            }).responseJSON.data;

        }
    };
}));
