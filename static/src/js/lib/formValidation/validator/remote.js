/**
 * remote validator
 */
(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("validator/remote", ["jquery", "base", "csrfToken"], factory);
    } else {
        // planted over the root!
        factory(root.jQuery, root.FormValidation);
    }
}(this, function ($, FormValidation, csrfTokenHeader) {
    FormValidation.I18n = $.extend(true, FormValidation.I18n || {}, {
        'en_US': {
            remote: {
                'default': ''
            }
        }
    });
    FormValidation.Validator.remote = {
        validate: function(validator, $field, options) {
            var dfd   = new $.Deferred(), ajaxData = {};
            ajaxData[options.field] = $field.val();
            if ($field.val() === '')
                return true;
            var url     = options.url;
            var xhr = $.ajax({
                beforeSend: csrfTokenHeader,
                url: url,
                dataType: 'json',
                data: ajaxData,
                method: "post"
            });
            xhr.success(function(response) {
                if (response.code == 1)
                    dfd.resolve($field, 'remote',{valid:true, message:options.msg});
                dfd.resolve($field, 'remote',{valid:!response.data, message:options.msg});
            })
            .error(function(response) {
                dfd.resolve($field, 'remote', {valid: false});
            });
            return dfd;
        }
    };
}));
