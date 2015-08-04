/**
 * confirm validator
 */

(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("validator/confirm", ["jquery", "base"], factory);
    } else {
        // planted over the root!
        factory(root.jQuery, root.FormValidation);
    }

}(this, function ($, FormValidation) {
    FormValidation.I18n = $.extend(true, FormValidation.I18n || {}, {
        'en_US': {
            confirm: {
                'default': 'Please input the same value'
            }
        }
    });

    FormValidation.Validator.confirm = {

        validate: function(validator, $field, options) {
                if (options.firstPassword.val() == options.secondPassword.val()  ||options.secondPassword.val()== '')
                    return true;
                return false;
            }
    };
}));
