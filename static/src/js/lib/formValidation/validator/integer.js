/**
 * integer validator
 *
 * @link        http://formvalidation.io/validators/integer/
 * @author      https://twitter.com/nghuuphuoc
 * @copyright   (c) 2013 - 2015 Nguyen Huu Phuoc
 * @license     http://formvalidation.io/license/
 */

(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("validator/integer", ["jquery", "base"], factory);
    } else {
        // planted over the root!
        factory(root.jQuery, root.FormValidation);
    }

}(this, function ($, FormValidation) {
    FormValidation.I18n = $.extend(true, FormValidation.I18n || {}, {
        'en_US': {
            integer: {
                'default': 'Please enter a valid number'
            }
        }
    });

    FormValidation.Validator.integer = {
        enableByHtml5: function($field) {
            return ('number' === $field.attr('type')) && ($field.attr('step') === undefined || $field.attr('step') % 1 === 0);
        },

        /**
         * Return true if the input value is an integer
         *
         * @param {FormValidation.Base} validator The validator plugin instance
         * @param {jQuery} $field Field element
         * @param {Object} options Can consist of the following key:
         * - message: The invalid message
         * @returns {Boolean}
         */
        validate: function(validator, $field, options) {
            if (this.enableByHtml5($field) && $field.get(0).validity && $field.get(0).validity.badInput === true) {
                return false;
            }

            var value = validator.getFieldValue($field, 'integer');
            if (value === '') {
                return true;
            }
            return /^(?:-?(?:0|[1-9][0-9]*))$/.test(value);
        }
    };


    return FormValidation.Validator.integer;
}));
