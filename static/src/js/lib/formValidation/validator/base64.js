/**
 * base64 validator
 *
 * @link        http://formvalidation.io/validators/base64/
 * @author      https://twitter.com/nghuuphuoc
 * @copyright   (c) 2013 - 2015 Nguyen Huu Phuoc
 * @license     http://formvalidation.io/license/
 */

(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("validator/XXXXXXXXXXXXXXXXXXXXXXXXXbase64", ["jquery", "base"], factory);
    } else {
        // planted over the root!
        factory(root.jQuery, root.FormValidation);
    }

}(this, function ($, FormValidation) {
    FormValidation.I18n = $.extend(true, FormValidation.I18n || {}, {
        'en_US': {
            base64: {
                'default': 'Please enter a valid base 64 encoded'
            }
        }
    });

    FormValidation.Validator.base64 = {
        /**
         * Return true if the input value is a base 64 encoded string.
         *
         * @param {FormValidation.Base} validator The validator plugin instance
         * @param {jQuery} $field Field element
         * @param {Object} options Can consist of the following keys:
         * - message: The invalid message
         * @returns {Boolean}
         */
        validate: function(validator, $field, options) {
            var value = validator.getFieldValue($field, 'base64');
            if (value === '') {
                return true;
            }

            return /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$/.test(value);
        }
    };

    return FormValidation.Validator.base64;
}));
