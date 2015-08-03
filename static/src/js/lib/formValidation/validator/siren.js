/**
 * siren validator
 *
 * @link        http://formvalidation.io/validators/siren/
 * @author      https://twitter.com/nghuuphuoc
 * @copyright   (c) 2013 - 2015 Nguyen Huu Phuoc
 * @license     http://formvalidation.io/license/
 */

(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("validator/siren", ["jquery", "base"], factory);
    } else {
        // planted over the root!
        factory(root.jQuery, root.FormValidation);
    }

}(this, function ($, FormValidation) {
    FormValidation.I18n = $.extend(true, FormValidation.I18n || {}, {
		'en_US': {
			siren: {
				'default': 'Please enter a valid SIREN number'
			}
		}
    });

	FormValidation.Validator.siren = {
		/**
		 * Check if a string is a siren number
		 *
		 * @param {FormValidation.Base} validator The validator plugin instance
		 * @param {jQuery} $field Field element
		 * @param {Object} options Consist of key:
         * - message: The invalid message
		 * @returns {Boolean}
		 */
		validate: function(validator, $field, options) {
			var value = validator.getFieldValue($field, 'siren');
			if (value === '') {
				return true;
			}

            if (!/^\d{9}$/.test(value)) {
                return false;
            }
            return FormValidation.Helper.luhn(value);
		}
	};


    return FormValidation.Validator.siren;
}));
