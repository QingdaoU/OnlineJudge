/**
 * remoteCSRF validator
 */
(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("validator/remoteCSRF", ["jquery", "base", "csrf"], factory);
    } else {
        // planted over the root!
        factory(root.jQuery, root.FormValidation);
    }
}(this, function ($, FormValidation, csrfHeader) {
    FormValidation.I18n = $.extend(true, FormValidation.I18n || {}, {
        'en_US': {
            remoteCSRF: {
                'default': ''
            }
        }
    });
    FormValidation.Validator.remoteCSRF = {
        validate: function(validator, $field, options) {
            var dfd   = new $.Deferred(), ajaxData = {};
            ajaxData[options.field] = $field.val();
            if ($field.val() === '')
                return true;
            var url     = options.url;
            var xhr = $.ajax({
                beforeSend: csrfHeader,
                url: url,
                dataType: 'json',
                data: ajaxData,
                method: "post"
            });
            xhr.success(function(response) {
                dfd.resolve($field, 'remoteCSRF',{valid:!response.data, message:options.msg});
            })
            .error(function(response) {
                dfd.resolve($field, 'remoteCSRF', {valid: false});
            });
            return dfd;
        }
    };
}));
