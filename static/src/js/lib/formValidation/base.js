/**
 * FormValidation (http://formvalidation.io)
 * The best jQuery plugin to validate form fields. Support Bootstrap, Foundation, Pure, SemanticUI, UIKit frameworks
 *
 * @author      https://twitter.com/nghuuphuoc
 * @copyright   (c) 2013 - 2015 Nguyen Huu Phuoc
 * @license     http://formvalidation.io/license/
 */

(function(root, factory) {

    "use strict";

    // AMD module is defined
    if (typeof define === "function" && define.amd) {
        define("base", ["jquery"], factory);
    } else {
        // planted over the root!
        root.FormValidation = factory(root.jQuery);
    }

}(this, function ($) {

    // Register the namespace
    var FormValidation = {
        AddOn:     {},  // Add-ons
        Framework: {},  // Supported frameworks
        I18n:      {},  // i18n
        Validator: {},  // Available validators
        Helper:    {}   // Helper object
    };

    if (typeof jQuery === 'undefined') {
        throw new Error('FormValidation requires jQuery');
    }

    // identify jquery version
    (function($) {
        var version = $.fn.jquery.split(' ')[0].split('.');
        if ((+version[0] < 2 && +version[1] < 9) || (+version[0] === 1 && +version[1] === 9 && +version[2] < 1)) {
            throw new Error('FormValidation requires jQuery version 1.9.1 or higher');
        }
    }(jQuery));

    (function($) {
        // TODO: Remove backward compatibility in v0.7.0
        /**
         * Constructor
         *
         * @param {jQuery|String} form The form element or selector
         * @param {Object} options The options
         * @param {String} [namespace] The optional namespace which is used for data-{namespace}-xxx attributes and internal data.
         * Currently, it's used to support backward version
         * @constructor
         */
        FormValidation.Base = function(form, options, namespace) {
            this.$form      = $(form);
            this.options    = $.extend({}, $.fn.formValidation.DEFAULT_OPTIONS, options);
            this._namespace = namespace || 'fv';

            this.$invalidFields = $([]);    // Array of invalid fields
            this.$submitButton  = null;     // The submit button which is clicked to submit form
            this.$hiddenButton  = null;

            // Validating status
            this.STATUS_NOT_VALIDATED = 'NOT_VALIDATED';
            this.STATUS_VALIDATING    = 'VALIDATING';
            this.STATUS_INVALID       = 'INVALID';
            this.STATUS_VALID         = 'VALID';

            // Determine the event that is fired when user change the field value
            // Most modern browsers supports input event except IE 7, 8.
            // IE 9 supports input event but the event is still not fired if I press the backspace key.
            // Get IE version
            // https://gist.github.com/padolsey/527683/#comment-7595
            var ieVersion = (function() {
                var v = 3, div = document.createElement('div'), a = div.all || [];
                while (div.innerHTML = '<!--[if gt IE '+(++v)+']><br><![endif]-->', a[0]) {}
                return v > 4 ? v : !v;
            }());

            var el = document.createElement('div');
            this._changeEvent = (ieVersion === 9 || !('oninput' in el)) ? 'keyup' : 'input';

            // The flag to indicate that the form is ready to submit when a remote/callback validator returns
            this._submitIfValid = null;

            // Field elements
            this._cacheFields = {};

            this._init();
        };

        FormValidation.Base.prototype = {
            constructor: FormValidation.Base,

            /**
             * Check if the number of characters of field value exceed the threshold or not
             *
             * @param {jQuery} $field The field element
             * @returns {Boolean}
             */
            _exceedThreshold: function($field) {
                var ns        = this._namespace,
                    field     = $field.attr('data-' + ns + '-field'),
                    threshold = this.options.fields[field].threshold || this.options.threshold;
                if (!threshold) {
                    return true;
                }
                var cannotType = $.inArray($field.attr('type'), ['button', 'checkbox', 'file', 'hidden', 'image', 'radio', 'reset', 'submit']) !== -1;
                return (cannotType || $field.val().length >= threshold);
            },

            /**
             * Init form
             */
            _init: function() {
                var that    = this,
                    ns      = this._namespace,
                    options = {
                        addOns:         {},
                        autoFocus:      this.$form.attr('data-' + ns + '-autofocus'),
                        button: {
                            selector: this.$form.attr('data-' + ns + '-button-selector') || this.$form.attr('data-' + ns + '-submitbuttons'), // Support backward
                            disabled: this.$form.attr('data-' + ns + '-button-disabled')
                        },
                        control: {
                            valid:   this.$form.attr('data-' + ns + '-control-valid'),
                            invalid: this.$form.attr('data-' + ns + '-control-invalid')
                        },
                        err: {
                            clazz:     this.$form.attr('data-' + ns + '-err-clazz'),
                            container: this.$form.attr('data-' + ns + '-err-container') || this.$form.attr('data-' + ns + '-container'), // Support backward
                            parent:    this.$form.attr('data-' + ns + '-err-parent')
                        },
                        events: {
                            formInit:         this.$form.attr('data-' + ns + '-events-form-init'),
                            formError:        this.$form.attr('data-' + ns + '-events-form-error'),
                            formSuccess:      this.$form.attr('data-' + ns + '-events-form-success'),
                            fieldAdded:       this.$form.attr('data-' + ns + '-events-field-added'),
                            fieldRemoved:     this.$form.attr('data-' + ns + '-events-field-removed'),
                            fieldInit:        this.$form.attr('data-' + ns + '-events-field-init'),
                            fieldError:       this.$form.attr('data-' + ns + '-events-field-error'),
                            fieldSuccess:     this.$form.attr('data-' + ns + '-events-field-success'),
                            fieldStatus:      this.$form.attr('data-' + ns + '-events-field-status'),
                            localeChanged:    this.$form.attr('data-' + ns + '-events-locale-changed'),
                            validatorError:   this.$form.attr('data-' + ns + '-events-validator-error'),
                            validatorSuccess: this.$form.attr('data-' + ns + '-events-validator-success')
                        },
                        excluded:      this.$form.attr('data-' + ns + '-excluded'),
                        icon: {
                            valid:      this.$form.attr('data-' + ns + '-icon-valid')      || this.$form.attr('data-' + ns + '-feedbackicons-valid'),      // Support backward
                            invalid:    this.$form.attr('data-' + ns + '-icon-invalid')    || this.$form.attr('data-' + ns + '-feedbackicons-invalid'),    // Support backward
                            validating: this.$form.attr('data-' + ns + '-icon-validating') || this.$form.attr('data-' + ns + '-feedbackicons-validating'), // Support backward
                            feedback:   this.$form.attr('data-' + ns + '-icon-feedback')
                        },
                        live:          this.$form.attr('data-' + ns + '-live'),
                        locale:        this.$form.attr('data-' + ns + '-locale'),
                        message:       this.$form.attr('data-' + ns + '-message'),
                        onError:       this.$form.attr('data-' + ns + '-onerror'),
                        onSuccess:     this.$form.attr('data-' + ns + '-onsuccess'),
                        row: {
                            selector: this.$form.attr('data-' + ns + '-row-selector') || this.$form.attr('data-' + ns + '-group'), // Support backward
                            valid:    this.$form.attr('data-' + ns + '-row-valid'),
                            invalid:  this.$form.attr('data-' + ns + '-row-invalid'),
                            feedback: this.$form.attr('data-' + ns + '-row-feedback')
                        },
                        threshold:     this.$form.attr('data-' + ns + '-threshold'),
                        trigger:       this.$form.attr('data-' + ns + '-trigger'),
                        verbose:       this.$form.attr('data-' + ns + '-verbose'),
                        fields:        {}
                    };

                this.$form
                    // Disable client side validation in HTML 5
                    .attr('novalidate', 'novalidate')
                    .addClass(this.options.elementClass)
                    // Disable the default submission first
                    .on('submit.' + ns, function(e) {
                        e.preventDefault();
                        that.validate();
                    })
                    .on('click.' + ns, this.options.button.selector, function() {
                        that.$submitButton  = $(this);
                        // The user just click the submit button
                        that._submitIfValid = true;
                    })
                    // Find all fields which have either "name" or "data-{namespace}-field" attribute
                    .find('[name], [data-' + ns + '-field]')
                        .each(function() {
                            var $field = $(this),
                                field  = $field.attr('name') || $field.attr('data-' + ns + '-field'),
                                opts   = that._parseOptions($field);
                            if (opts) {
                                $field.attr('data-' + ns + '-field', field);
                                options.fields[field] = $.extend({}, opts, options.fields[field]);
                            }
                        });

                this.options = $.extend(true, this.options, options);

                // Normalize the err.parent option
                if ('string' === typeof this.options.err.parent) {
                    this.options.err.parent = new RegExp(this.options.err.parent);
                }

                // Support backward
                if (this.options.container) {
                    this.options.err.container = this.options.container;
                    delete this.options.container;
                }
                if (this.options.feedbackIcons) {
                    this.options.icon = $.extend(true, this.options.icon, this.options.feedbackIcons);
                    delete this.options.feedbackIcons;
                }
                if (this.options.group) {
                    this.options.row.selector = this.options.group;
                    delete this.options.group;
                }
                if (this.options.submitButtons) {
                    this.options.button.selector = this.options.submitButtons;
                    delete this.options.submitButtons;
                }

                // If the locale is not found, reset it to default one
                if (!FormValidation.I18n[this.options.locale]) {
                    this.options.locale = $.fn.formValidation.DEFAULT_OPTIONS.locale;
                }

                // Parse the add-on options from HTML attributes
                this.options = $.extend(true, this.options, { addOns: this._parseAddOnOptions() });

                // When pressing Enter on any field in the form, the first submit button will do its job.
                // The form then will be submitted.
                // I create a first hidden submit button
                this.$hiddenButton = $('<button/>')
                                        .attr('type', 'submit')
                                        .prependTo(this.$form)
                                        .addClass('fv-hidden-submit')
                                        .css({ display: 'none', width: 0, height: 0 });

                this.$form
                    .on('click.' +  this._namespace, '[type="submit"]', function(e) {
                        // #746: Check if the button click handler returns false
                        if (!e.isDefaultPrevented()) {
                            var $target = $(e.target),
                                // The button might contain HTML tag
                                $button = $target.is('[type="submit"]') ? $target.eq(0) : $target.parent('[type="submit"]').eq(0);

                            // Don't perform validation when clicking on the submit button/input
                            // which aren't defined by the 'button.selector' option
                            if (that.options.button.selector && !$button.is(that.options.button.selector) && !$button.is(that.$hiddenButton)) {
                                that.$form.off('submit.' + that._namespace).submit();
                            }
                        }
                    });

                for (var field in this.options.fields) {
                    this._initField(field);
                }

                // Init the add-ons
                for (var addOn in this.options.addOns) {
                    if ('function' === typeof FormValidation.AddOn[addOn].init) {
                        FormValidation.AddOn[addOn].init(this, this.options.addOns[addOn]);
                    }
                }

                this.$form.trigger($.Event(this.options.events.formInit), {
                    bv: this,   // Support backward
                    fv: this,
                    options: this.options
                });

                // Prepare the events
                if (this.options.onSuccess) {
                    this.$form.on(this.options.events.formSuccess, function(e) {
                        FormValidation.Helper.call(that.options.onSuccess, [e]);
                    });
                }
                if (this.options.onError) {
                    this.$form.on(this.options.events.formError, function(e) {
                        FormValidation.Helper.call(that.options.onError, [e]);
                    });
                }
            },

            /**
             * Init field
             *
             * @param {String|jQuery} field The field name or field element
             */
            _initField: function(field) {
                var ns     = this._namespace,
                    fields = $([]);
                switch (typeof field) {
                    case 'object':
                        fields = field;
                        field  = field.attr('data-' + ns + '-field');
                        break;
                    case 'string':
                        fields = this.getFieldElements(field);
                        fields.attr('data-' + ns + '-field', field);
                        break;
                    default:
                        break;
                }

                // We don't need to validate non-existing fields
                if (fields.length === 0) {
                    return;
                }

                if (this.options.fields[field] === null || this.options.fields[field].validators === null) {
                    return;
                }

                var validatorName;
                for (validatorName in this.options.fields[field].validators) {
                    if (!FormValidation.Validator[validatorName]) {
                        delete this.options.fields[field].validators[validatorName];
                    }
                }
                if (this.options.fields[field].enabled === null) {
                    this.options.fields[field].enabled = true;
                }

                var that      = this,
                    total     = fields.length,
                    type      = fields.attr('type'),
                    updateAll = (total === 1) || ('radio' === type) || ('checkbox' === type),
                    trigger   = this._getFieldTrigger(fields.eq(0)),
                    events    = $.map(trigger, function(item) {
                        return item + '.update.' + ns;
                    }).join(' ');

                for (var i = 0; i < total; i++) {
                    var $field    = fields.eq(i),
                        row       = this.options.fields[field].row || this.options.row.selector,
                        $parent   = $field.closest(row),
                        // Allow user to indicate where the error messages are shown
                        // Support backward
                        container = ('function' === typeof (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container))
                                    ? (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container).call(this, $field, this)
                                    : (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container),
                        $message  = (container && container !== 'tooltip' && container !== 'popover') ? $(container) : this._getMessageContainer($field, row);

                    if (container && container !== 'tooltip' && container !== 'popover') {
                        $message.addClass(this.options.err.clazz);
                    }

                    // Remove all error messages and feedback icons
                    $message.find('.' + this.options.err.clazz.split(' ').join('.') + '[data-' + ns + '-validator][data-' + ns + '-for="' + field + '"]').remove();
                    $parent.find('i[data-' + ns + '-icon-for="' + field + '"]').remove();

                    // Whenever the user change the field value, mark it as not validated yet
                    $field.off(events).on(events, function() {
                        that.updateStatus($(this), that.STATUS_NOT_VALIDATED);
                    });

                    // Create help block elements for showing the error messages
                    $field.data(ns + '.messages', $message);
                    for (validatorName in this.options.fields[field].validators) {
                        $field.data(ns + '.result.' + validatorName, this.STATUS_NOT_VALIDATED);

                        if (!updateAll || i === total - 1) {
                            $('<small/>')
                                .css('display', 'none')
                                .addClass(this.options.err.clazz)
                                .attr('data-' + ns + '-validator', validatorName)
                                .attr('data-' + ns + '-for', field)
                                .attr('data-' + ns + '-result', this.STATUS_NOT_VALIDATED)
                                .html(this._getMessage(field, validatorName))
                                .appendTo($message);
                        }

                        // Init the validator
                        if ('function' === typeof FormValidation.Validator[validatorName].init) {
                            FormValidation.Validator[validatorName].init(this, $field, this.options.fields[field].validators[validatorName]);
                        }
                    }

                    // Prepare the feedback icons
                    // Available from Bootstrap 3.1 (http://getbootstrap.com/css/#forms-control-validation)
                    if (this.options.fields[field].icon !== false && this.options.fields[field].icon !== 'false'
                        && this.options.icon
                        && this.options.icon.valid && this.options.icon.invalid && this.options.icon.validating
                        && (!updateAll || i === total - 1))
                    {
                        // $parent.removeClass(this.options.row.valid).removeClass(this.options.row.invalid).addClass(this.options.row.feedback);
                        // Keep error messages which are populated from back-end
                        $parent.addClass(this.options.row.feedback);
                        var $icon = $('<i/>')
                                        .css('display', 'none')
                                        .addClass(this.options.icon.feedback)
                                        .attr('data-' + ns + '-icon-for', field)
                                        .insertAfter($field);

                        // Store the icon as a data of field element
                        (!updateAll ? $field : fields).data(ns + '.icon', $icon);

                        if ('tooltip' === container || 'popover' === container) {
                            (!updateAll ? $field : fields)
                                .on(this.options.events.fieldError, function() {
                                    $parent.addClass('fv-has-tooltip');
                                })
                                .on(this.options.events.fieldSuccess, function() {
                                    $parent.removeClass('fv-has-tooltip');
                                });

                            $field
                                // Show tooltip/popover message when field gets focus
                                .off('focus.container.' + ns)
                                .on('focus.container.' + ns, function() {
                                    that._showTooltip($field, container);
                                })
                                // and hide them when losing focus
                                .off('blur.container.' + ns)
                                .on('blur.container.' + ns, function() {
                                    that._hideTooltip($field, container);
                                });
                        }

                        if ('string' === typeof this.options.fields[field].icon && this.options.fields[field].icon !== 'true') {
                            $icon.appendTo($(this.options.fields[field].icon));
                        } else {
                            this._fixIcon($field, $icon);
                        }
                    }
                }

                // Prepare the events
                fields
                    .on(this.options.events.fieldSuccess, function(e, data) {
                        var onSuccess = that.getOptions(data.field, null, 'onSuccess');
                        if (onSuccess) {
                            FormValidation.Helper.call(onSuccess, [e, data]);
                        }
                    })
                    .on(this.options.events.fieldError, function(e, data) {
                        var onError = that.getOptions(data.field, null, 'onError');
                        if (onError) {
                            FormValidation.Helper.call(onError, [e, data]);
                        }
                    })
                    .on(this.options.events.fieldStatus, function(e, data) {
                        var onStatus = that.getOptions(data.field, null, 'onStatus');
                        if (onStatus) {
                            FormValidation.Helper.call(onStatus, [e, data]);
                        }
                    })
                    .on(this.options.events.validatorError, function(e, data) {
                        var onError = that.getOptions(data.field, data.validator, 'onError');
                        if (onError) {
                            FormValidation.Helper.call(onError, [e, data]);
                        }
                    })
                    .on(this.options.events.validatorSuccess, function(e, data) {
                        var onSuccess = that.getOptions(data.field, data.validator, 'onSuccess');
                        if (onSuccess) {
                            FormValidation.Helper.call(onSuccess, [e, data]);
                        }
                    });

                // Set live mode
                this.onLiveChange(fields, 'live', function() {
                    if (that._exceedThreshold($(this))) {
                        that.validateField($(this));
                    }
                });

                fields.trigger($.Event(this.options.events.fieldInit), {
                    bv: this,   // Support backward
                    fv: this,
                    field: field,
                    element: fields
                });
            },

            /**
             * Check if the field is excluded.
             * Returning true means that the field will not be validated
             *
             * @param {jQuery} $field The field element
             * @returns {Boolean}
             */
            _isExcluded: function($field) {
                var ns           = this._namespace,
                    excludedAttr = $field.attr('data-' + ns + '-excluded'),
                    // I still need to check the 'name' attribute while initializing the field
                    field        = $field.attr('data-' + ns + '-field') || $field.attr('name');

                switch (true) {
                    case (!!field && this.options.fields && this.options.fields[field] && (this.options.fields[field].excluded === 'true' || this.options.fields[field].excluded === true)):
                    case (excludedAttr === 'true'):
                    case (excludedAttr === ''):
                        return true;

                    case (!!field && this.options.fields && this.options.fields[field] && (this.options.fields[field].excluded === 'false' || this.options.fields[field].excluded === false)):
                    case (excludedAttr === 'false'):
                        return false;

                    default:
                        if (this.options.excluded) {
                            // Convert to array first
                            if ('string' === typeof this.options.excluded) {
                                this.options.excluded = $.map(this.options.excluded.split(','), function(item) {
                                    // Trim the spaces
                                    return $.trim(item);
                                });
                            }

                            var length = this.options.excluded.length;
                            for (var i = 0; i < length; i++) {
                                if (('string' === typeof this.options.excluded[i] && $field.is(this.options.excluded[i]))
                                    || ('function' === typeof this.options.excluded[i] && this.options.excluded[i].call(this, $field, this) === true))
                                {
                                    return true;
                                }
                            }
                        }
                        return false;
                }
            },

            /**
             * Get a field changed trigger event
             *
             * @param {jQuery} $field The field element
             * @returns {String[]} The event names triggered on field change
             */
            _getFieldTrigger: function($field) {
                var ns      = this._namespace,
                    trigger = $field.data(ns + '.trigger');
                if (trigger) {
                    return trigger;
                }

                var type  = $field.attr('type'),
                    name  = $field.attr('data-' + ns + '-field'),
                    event = ('radio' === type || 'checkbox' === type || 'file' === type || 'SELECT' === $field.get(0).tagName) ? 'change' : this._changeEvent;
                trigger   = ((this.options.fields[name] ? this.options.fields[name].trigger : null) || this.options.trigger || event).split(' ');

                // Since the trigger data is used many times, I need to cache it to use later
                $field.data(ns + '.trigger', trigger);

                return trigger;
            },

            /**
             * Get the error message for given field and validator
             *
             * @param {String} field The field name
             * @param {String} validatorName The validator name
             * @returns {String}
             */
            _getMessage: function(field, validatorName) {
                if (!this.options.fields[field] || !FormValidation.Validator[validatorName]
                    || !this.options.fields[field].validators || !this.options.fields[field].validators[validatorName])
                {
                    return '';
                }

                switch (true) {
                    case !!this.options.fields[field].validators[validatorName].message:
                        return this.options.fields[field].validators[validatorName].message;
                    case !!this.options.fields[field].message:
                        return this.options.fields[field].message;
                    case !!FormValidation.I18n[this.options.locale][validatorName]['default']:
                        return FormValidation.I18n[this.options.locale][validatorName]['default'];
                    default:
                        return this.options.message;
                }
            },

            /**
             * Get the element to place the error messages
             *
             * @param {jQuery} $field The field element
             * @param {String} row
             * @returns {jQuery}
             */
            _getMessageContainer: function($field, row) {
                if (!this.options.err.parent) {
                    throw new Error('The err.parent option is not defined');
                }

                var $parent = $field.parent();
                if ($parent.is(row)) {
                    return $parent;
                }

                var cssClasses = $parent.attr('class');
                if (!cssClasses) {
                    return this._getMessageContainer($parent, row);
                }

                if (this.options.err.parent.test(cssClasses)) {
                    return $parent;
                }

                return this._getMessageContainer($parent, row);
            },

            /**
             * Parse the add-on options from HTML attributes
             *
             * @returns {Object}
             */
            _parseAddOnOptions: function() {
                var ns     = this._namespace,
                    names  = this.$form.attr('data-' + ns + '-addons'),
                    addOns = this.options.addOns || {};

                if (names) {
                    names = names.replace(/\s/g, '').split(',');
                    for (var i = 0; i < names.length; i++) {
                        if (!addOns[names[i]]) {
                            addOns[names[i]] = {};
                        }
                    }
                }

                // Try to parse each add-on options
                var addOn, attrMap, attr, option;
                for (addOn in addOns) {
                    if (!FormValidation.AddOn[addOn]) {
                        // Add-on is not found
                        delete addOns[addOn];
                        continue;
                    }

                    attrMap = FormValidation.AddOn[addOn].html5Attributes;
                    if (attrMap) {
                        for (attr in attrMap) {
                            option = this.$form.attr('data-' + ns + '-addons-' + addOn.toLowerCase() + '-' + attr.toLowerCase());
                            if (option) {
                                addOns[addOn][attrMap[attr]] = option;
                            }
                        }
                    }
                }

                return addOns;
            },

            /**
             * Parse the validator options from HTML attributes
             *
             * @param {jQuery} $field The field element
             * @returns {Object}
             */
            _parseOptions: function($field) {
                var ns         = this._namespace,
                    field      = $field.attr('name') || $field.attr('data-' + ns + '-field'),
                    validators = {},
                    validator,
                    v,          // Validator name
                    attrName,
                    enabled,
                    optionName,
                    optionAttrName,
                    optionValue,
                    html5AttrName,
                    html5AttrMap;

                for (v in FormValidation.Validator) {
                    validator    = FormValidation.Validator[v];
                    attrName     = 'data-' + ns + '-' + v.toLowerCase(),
                    enabled      = $field.attr(attrName) + '';
                    html5AttrMap = ('function' === typeof validator.enableByHtml5) ? validator.enableByHtml5($field) : null;

                    if ((html5AttrMap && enabled !== 'false')
                        || (html5AttrMap !== true && ('' === enabled || 'true' === enabled || attrName === enabled.toLowerCase())))
                    {
                        // Try to parse the options via attributes
                        validator.html5Attributes = $.extend({}, {
                                                        message: 'message',
                                                        onerror: 'onError',
                                                        onsuccess: 'onSuccess',
                                                        transformer: 'transformer'
                                                    }, validator.html5Attributes);
                        validators[v] = $.extend({}, html5AttrMap === true ? {} : html5AttrMap, validators[v]);

                        for (html5AttrName in validator.html5Attributes) {
                            optionName  = validator.html5Attributes[html5AttrName];
                            optionAttrName = 'data-' + ns + '-' + v.toLowerCase() + '-' + html5AttrName,
                            optionValue = $field.attr(optionAttrName);
                            if (optionValue) {
                                if ('true' === optionValue || optionAttrName === optionValue.toLowerCase()) {
                                    optionValue = true;
                                } else if ('false' === optionValue) {
                                    optionValue = false;
                                }
                                validators[v][optionName] = optionValue;
                            }
                        }
                    }
                }

                var opts = {
                        autoFocus:   $field.attr('data-' + ns + '-autofocus'),
                        err:         $field.attr('data-' + ns + '-err-container') || $field.attr('data-' + ns + '-container'), // Support backward
                        excluded:    $field.attr('data-' + ns + '-excluded'),
                        icon:        $field.attr('data-' + ns + '-icon') || $field.attr('data-' + ns + '-feedbackicons') || (this.options.fields && this.options.fields[field] ? this.options.fields[field].feedbackIcons : null), // Support backward
                        message:     $field.attr('data-' + ns + '-message'),
                        onError:     $field.attr('data-' + ns + '-onerror'),
                        onStatus:    $field.attr('data-' + ns + '-onstatus'),
                        onSuccess:   $field.attr('data-' + ns + '-onsuccess'),
                        row:         $field.attr('data-' + ns + '-row') || $field.attr('data-' + ns + '-group') || (this.options.fields && this.options.fields[field] ? this.options.fields[field].group : null), // Support backward
                        selector:    $field.attr('data-' + ns + '-selector'),
                        threshold:   $field.attr('data-' + ns + '-threshold'),
                        transformer: $field.attr('data-' + ns + '-transformer'),
                        trigger:     $field.attr('data-' + ns + '-trigger'),
                        verbose:     $field.attr('data-' + ns + '-verbose'),
                        validators:  validators
                    },
                    emptyOptions    = $.isEmptyObject(opts),        // Check if the field options are set using HTML attributes
                    emptyValidators = $.isEmptyObject(validators);  // Check if the field validators are set using HTML attributes

                if (!emptyValidators || (!emptyOptions && this.options.fields && this.options.fields[field])) {
                    opts.validators = validators;
                    return opts;
                } else {
                    return null;
                }
            },

            /**
             * Called when all validations are completed
             */
            _submit: function() {
                var isValid   = this.isValid(),
                    eventType = isValid ? this.options.events.formSuccess : this.options.events.formError,
                    e         = $.Event(eventType);

                this.$form.trigger(e);

                // Call default handler
                // Check if whether the submit button is clicked
                if (this.$submitButton) {
                    isValid ? this._onSuccess(e) : this._onError(e);
                }
            },

            // ~~~~~~
            // Events
            // ~~~~~~

            /**
             * The default handler of error.form.fv event.
             * It will be called when there is a invalid field
             *
             * @param {jQuery.Event} e The jQuery event object
             */
            _onError: function(e) {
                if (e.isDefaultPrevented()) {
                    return;
                }

                if ('submitted' === this.options.live) {
                    // Enable live mode
                    this.options.live = 'enabled';

                    var that = this;
                    for (var field in this.options.fields) {
                        (function(f) {
                            var fields  = that.getFieldElements(f);
                            if (fields.length) {
                                that.onLiveChange(fields, 'live', function() {
                                    if (that._exceedThreshold($(this))) {
                                        that.validateField($(this));
                                    }
                                });
                            }
                        })(field);
                    }
                }

                // Determined the first invalid field which will be focused on automatically
                var ns = this._namespace;
                for (var i = 0; i < this.$invalidFields.length; i++) {
                    var $field    = this.$invalidFields.eq(i),
                        autoFocus = this.isOptionEnabled($field.attr('data-' + ns + '-field'), 'autoFocus');
                    if (autoFocus) {
                        // Focus the field
                        $field.focus();
                        break;
                    }
                }
            },

            /**
             * Called after validating a field element
             *
             * @param {jQuery} $field The field element
             * @param {String} [validatorName] The validator name
             */
            _onFieldValidated: function($field, validatorName) {
                var ns            = this._namespace,
                    field         = $field.attr('data-' + ns + '-field'),
                    validators    = this.options.fields[field].validators,
                    counter       = {},
                    numValidators = 0,
                    data          = {
                        bv: this,   // Support backward
                        fv: this,
                        field: field,
                        element: $field,
                        validator: validatorName,
                        result: $field.data(ns + '.response.' + validatorName)
                    };

                // Trigger an event after given validator completes
                if (validatorName) {
                    switch ($field.data(ns + '.result.' + validatorName)) {
                        case this.STATUS_INVALID:
                            $field.trigger($.Event(this.options.events.validatorError), data);
                            break;
                        case this.STATUS_VALID:
                            $field.trigger($.Event(this.options.events.validatorSuccess), data);
                            break;
                        default:
                            break;
                    }
                }

                counter[this.STATUS_NOT_VALIDATED] = 0;
                counter[this.STATUS_VALIDATING]    = 0;
                counter[this.STATUS_INVALID]       = 0;
                counter[this.STATUS_VALID]         = 0;

                for (var v in validators) {
                    if (validators[v].enabled === false) {
                        continue;
                    }

                    numValidators++;
                    var result = $field.data(ns + '.result.' + v);
                    if (result) {
                        counter[result]++;
                    }
                }

                if (counter[this.STATUS_VALID] === numValidators) {
                    // Remove from the list of invalid fields
                    this.$invalidFields = this.$invalidFields.not($field);

                    $field.trigger($.Event(this.options.events.fieldSuccess), data);
                }
                // If all validators are completed and there is at least one validator which doesn't pass
                else if ((counter[this.STATUS_NOT_VALIDATED] === 0 || !this.isOptionEnabled(field, 'verbose')) && counter[this.STATUS_VALIDATING] === 0 && counter[this.STATUS_INVALID] > 0) {
                    // Add to the list of invalid fields
                    this.$invalidFields = this.$invalidFields.add($field);

                    $field.trigger($.Event(this.options.events.fieldError), data);
                }
            },

            /**
             * The default handler of success.form.fv event.
             * It will be called when all the fields are valid
             *
             * @param {jQuery.Event} e The jQuery event object
             */
            _onSuccess: function(e) {
                if (e.isDefaultPrevented()) {
                    return;
                }

                // Submit the form
                this.disableSubmitButtons(true).defaultSubmit();
            },

            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            // Abstract methods
            // Need to be implemented by sub-class that supports specific framework
            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            /**
             * Specific framework might need to adjust the icon position
             *
             * @param {jQuery} $field The field element
             * @param {jQuery} $icon The icon element
             */
            _fixIcon: function($field, $icon) {
            },

            /**
             * Create a tooltip or popover
             * It will be shown when focusing on the field
             *
             * @param {jQuery} $field The field element
             * @param {String} message The message
             * @param {String} type Can be 'tooltip' or 'popover'
             */
            _createTooltip: function($field, message, type) {
            },

            /**
             * Destroy the tooltip or popover
             *
             * @param {jQuery} $field The field element
             * @param {String} type Can be 'tooltip' or 'popover'
             */
            _destroyTooltip: function($field, type) {
            },

            /**
             * Hide a tooltip or popover
             *
             * @param {jQuery} $field The field element
             * @param {String} type Can be 'tooltip' or 'popover'
             */
            _hideTooltip: function($field, type) {
            },

            /**
             * Show a tooltip or popover
             *
             * @param {jQuery} $field The field element
             * @param {String} type Can be 'tooltip' or 'popover'
             */
            _showTooltip: function($field, type) {
            },

            // ~~~~~~~~~~~~~~
            // Public methods
            // ~~~~~~~~~~~~~~

            /**
             * Submit the form using default submission.
             * It also does not perform any validations when submitting the form
             */
            defaultSubmit: function() {
                var ns = this._namespace;
                if (this.$submitButton) {
                    // Create hidden input to send the submit buttons
                    $('<input/>')
                        .attr({
                            'type': 'hidden',
                            name: this.$submitButton.attr('name')
                        })
                        .attr('data-' + ns + '-submit-hidden', '')
                        .val(this.$submitButton.val())
                        .appendTo(this.$form);
                }

                // Submit form
                this.$form.off('submit.' + ns).submit();
            },

            /**
             * Disable/enable submit buttons
             *
             * @param {Boolean} disabled Can be true or false
             * @returns {FormValidation.Base}
             */
            disableSubmitButtons: function(disabled) {
                if (!disabled) {
                    this.$form
                        .find(this.options.button.selector)
                            .removeAttr('disabled')
                            .removeClass(this.options.button.disabled);
                } else if (this.options.live !== 'disabled') {
                    // Don't disable if the live validating mode is disabled
                    this.$form
                        .find(this.options.button.selector)
                            .attr('disabled', 'disabled')
                            .addClass(this.options.button.disabled);
                }

                return this;
            },

            /**
             * Retrieve the field elements by given name
             *
             * @param {String} field The field name
             * @returns {null|jQuery[]}
             */
            getFieldElements: function(field) {
                if (!this._cacheFields[field]) {
                    if (this.options.fields[field] && this.options.fields[field].selector) {
                        // Look for the field inside the form first
                        var f = this.$form.find(this.options.fields[field].selector);
                        // If not found, search in entire document
                        this._cacheFields[field] = f.length ? f : $(this.options.fields[field].selector);
                    } else {
                        this._cacheFields[field] = this.$form.find('[name="' + field + '"]');
                    }
                }

                return this._cacheFields[field];
            },

            /**
             * Get the field value after applying transformer
             *
             * @param {String|jQuery} field The field name or field element
             * @param {String} validatorName The validator name
             * @returns {String}
             */
            getFieldValue: function(field, validatorName) {
                var $field, ns = this._namespace;
                if ('string' === typeof field) {
                    $field = this.getFieldElements(field);
                    if ($field.length === 0) {
                        return null;
                    }
                } else {
                    $field = field;
                    field  = $field.attr('data-' + ns + '-field');
                }

                if (!field || !this.options.fields[field]) {
                    return $field.val();
                }

                var transformer = (this.options.fields[field].validators && this.options.fields[field].validators[validatorName]
                                    ? this.options.fields[field].validators[validatorName].transformer : null)
                                    || this.options.fields[field].transformer;
                return transformer ? FormValidation.Helper.call(transformer, [$field, validatorName]) : $field.val();
            },

            /**
             * Get the namespace
             *
             * @returns {String}
             */
            getNamespace: function() {
                return this._namespace;
            },

            /**
             * Get the field options
             *
             * @param {String|jQuery} [field] The field name or field element. If it is not set, the method returns the form options
             * @param {String} [validator] The name of validator. It null, the method returns form options
             * @param {String} [option] The option name
             * @return {String|Object}
             */
            getOptions: function(field, validator, option) {
                var ns = this._namespace;
                if (!field) {
                    return option ? this.options[option] : this.options;
                }
                if ('object' === typeof field) {
                    field = field.attr('data-' + ns + '-field');
                }
                if (!this.options.fields[field]) {
                    return null;
                }

                var options = this.options.fields[field];
                if (!validator) {
                    return option ? options[option] : options;
                }
                if (!options.validators || !options.validators[validator]) {
                    return null;
                }

                return option ? options.validators[validator][option] : options.validators[validator];
            },

            /**
             * Get the validating result of field
             *
             * @param {String|jQuery} field The field name or field element
             * @param {String} validatorName The validator name
             * @returns {String} The status. Can be 'NOT_VALIDATED', 'VALIDATING', 'INVALID' or 'VALID'
             */
            getStatus: function(field, validatorName) {
                var ns = this._namespace;
                switch (typeof field) {
                    case 'object':
                        return field.data(ns + '.result.' + validatorName);
                    case 'string':
                    /* falls through */
                    default:
                        return this.getFieldElements(field).eq(0).data(ns + '.result.' + validatorName);
                }
            },

            /**
             * Check whether or not a field option is enabled
             *
             * @param {String} field The field name
             * @param {String} option The option name, "verbose", "autoFocus", for example
             * @returns {Boolean}
             */
            isOptionEnabled: function(field, option) {
                if (this.options.fields[field] && (this.options.fields[field][option] === 'true' || this.options.fields[field][option] === true)) {
                    return true;
                }
                if (this.options.fields[field] && (this.options.fields[field][option] === 'false' || this.options.fields[field][option] === false)) {
                    return false;
                }
                return this.options[option] === 'true' || this.options[option] === true;
            },

            /**
             * Check the form validity
             *
             * @returns {Boolean}
             */
            isValid: function() {
                for (var field in this.options.fields) {
                    if (!this.isValidField(field)) {
                        return false;
                    }
                }

                return true;
            },

            /**
             * Check if all fields inside a given container are valid.
             * It's useful when working with a wizard-like such as tab, collapse
             *
             * @param {String|jQuery} container The container selector or element
             * @returns {Boolean|null} Returns one of three values
             * - true, if all fields inside the container are valid
             * - false, if there is one invalid field inside the container
             * - null, if the container consists of at least one field which is not validated yet or being validated
             */
            isValidContainer: function(container) {
                var that       = this,
                    ns         = this._namespace,
                    map        = {},
                    $container = ('string' === typeof container) ? $(container) : container;
                if ($container.length === 0) {
                    return true;
                }

                $container.find('[data-' + ns + '-field]').each(function() {
                    var $field = $(this),
                        field  = $field.attr('data-' + ns + '-field');
                    if (!that._isExcluded($field) && !map[field]) {
                        map[field] = $field;
                    }
                });

                for (var field in map) {
                    var $f      = map[field],
                        $errors = $f.data(ns + '.messages')
                                    .find('.' + this.options.err.clazz.split(' ').join('.') + '[data-' + ns + '-validator][data-' + ns + '-for="' + field + '"]');

                    if ($errors.filter('[data-' + ns + '-result="' + this.STATUS_INVALID + '"]').length > 0) {
                        return false;
                    }

                    // If the field is not validated
                    if ($errors.filter('[data-' + ns + '-result="' + this.STATUS_NOT_VALIDATED + '"]').length > 0
                        || $errors.filter('[data-' + ns + '-result="' + this.STATUS_VALIDATING + '"]').length > 0)
                    {
                        return null;
                    }
                }

                return true;
            },

            /**
             * Check if the field is valid or not
             *
             * @param {String|jQuery} field The field name or field element
             * @returns {Boolean}
             */
            isValidField: function(field) {
                var ns     = this._namespace,
                    fields = $([]);
                switch (typeof field) {
                    case 'object':
                        fields = field;
                        field  = field.attr('data-' + ns + '-field');
                        break;
                    case 'string':
                        fields = this.getFieldElements(field);
                        break;
                    default:
                        break;
                }
                if (fields.length === 0 || !this.options.fields[field] || this.options.fields[field].enabled === false) {
                    return true;
                }

                var type  = fields.attr('type'),
                    total = ('radio' === type || 'checkbox' === type) ? 1 : fields.length,
                    $field, validatorName, status;
                for (var i = 0; i < total; i++) {
                    $field = fields.eq(i);
                    if (this._isExcluded($field)) {
                        continue;
                    }

                    for (validatorName in this.options.fields[field].validators) {
                        if (this.options.fields[field].validators[validatorName].enabled === false) {
                            continue;
                        }

                        status = $field.data(ns + '.result.' + validatorName);
                        if (status !== this.STATUS_VALID) {
                            return false;
                        }
                    }
                }

                return true;
            },

            /**
             * Detach a handler function for a field live change event
             *
             * @param {jQuery[]} $fields The field elements
             * @param {String} namespace The event namespace
             * @returns {FormValidation.Base}
             */
            offLiveChange: function($fields, namespace) {
                if ($fields === null || $fields.length === 0) {
                    return this;
                }

                var ns      = this._namespace,
                    trigger = this._getFieldTrigger($fields.eq(0)),
                    events  = $.map(trigger, function(item) {
                        return item + '.' + namespace + '.' + ns;
                    }).join(' ');

                $fields.off(events);
                return this;
            },

            /**
             * Attach a handler function for a field live change event
             *
             * @param {jQuery[]} $fields The field elements
             * @param {String} namespace The event namespace
             * @param {Function} handler The handler function
             * @returns {FormValidation.Base}
             */
            onLiveChange: function($fields, namespace, handler) {
                if ($fields === null || $fields.length === 0) {
                    return this;
                }

                var ns      = this._namespace,
                    trigger = this._getFieldTrigger($fields.eq(0)),
                    events  = $.map(trigger, function(item) {
                        return item + '.' + namespace + '.' + ns;
                    }).join(' ');

                switch (this.options.live) {
                    case 'submitted':
                        break;
                    case 'disabled':
                        $fields.off(events);
                        break;
                    case 'enabled':
                    /* falls through */
                    default:
                        $fields.off(events).on(events, function(e) {
                            handler.apply(this, arguments);
                        });
                        break;
                }

                return this;
            },

            /**
             * Update the error message
             *
             * @param {String|jQuery} field The field name or field element
             * @param {String} validator The validator name
             * @param {String} message The message
             * @returns {FormValidation.Base}
             */
            updateMessage: function(field, validator, message) {
                var that    = this,
                    ns      = this._namespace,
                    $fields = $([]);
                switch (typeof field) {
                    case 'object':
                        $fields = field;
                        field   = field.attr('data-' + ns + '-field');
                        break;
                    case 'string':
                        $fields = this.getFieldElements(field);
                        break;
                    default:
                        break;
                }

                $fields.each(function() {
                    $(this)
                        .data(ns + '.messages')
                        .find('.' + that.options.err.clazz + '[data-' + ns + '-validator="' + validator + '"][data-' + ns + '-for="' + field + '"]').html(message);
                });
            },

            /**
             * Update all validating results of field
             *
             * @param {String|jQuery} field The field name or field element
             * @param {String} status The status. Can be 'NOT_VALIDATED', 'VALIDATING', 'INVALID' or 'VALID'
             * @param {String} [validatorName] The validator name. If null, the method updates validity result for all validators
             * @returns {FormValidation.Base}
             */
            updateStatus: function(field, status, validatorName) {
                var ns     = this._namespace,
                    fields = $([]);
                switch (typeof field) {
                    case 'object':
                        fields = field;
                        field  = field.attr('data-' + ns + '-field');
                        break;
                    case 'string':
                        fields = this.getFieldElements(field);
                        break;
                    default:
                        break;
                }

                if (!field || !this.options.fields[field]) {
                    return this;
                }

                if (status === this.STATUS_NOT_VALIDATED) {
                    // Reset the flag
                    // To prevent the form from doing submit when a deferred validator returns true while typing
                    this._submitIfValid = false;
                }

                var that  = this,
                    type  = fields.attr('type'),
                    row   = this.options.fields[field].row || this.options.row.selector,
                    total = ('radio' === type || 'checkbox' === type) ? 1 : fields.length;

                for (var i = 0; i < total; i++) {
                    var $field       = fields.eq(i);
                    if (this._isExcluded($field)) {
                        continue;
                    }

                    var $parent      = $field.closest(row),
                        $message     = $field.data(ns + '.messages'),
                        $allErrors   = $message.find('.' + this.options.err.clazz.split(' ').join('.') + '[data-' + ns + '-validator][data-' + ns + '-for="' + field + '"]'),
                        $errors      = validatorName ? $allErrors.filter('[data-' + ns + '-validator="' + validatorName + '"]') : $allErrors,
                        $icon        = $field.data(ns + '.icon'),
                        // Support backward
                        container    = ('function' === typeof (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container))
                                        ? (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container).call(this, $field, this)
                                        : (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container),
                        isValidField = null;

                    // Update status
                    if (validatorName) {
                        $field.data(ns + '.result.' + validatorName, status);
                    } else {
                        for (var v in this.options.fields[field].validators) {
                            $field.data(ns + '.result.' + v, status);
                        }
                    }

                    // Show/hide error elements and feedback icons
                    $errors.attr('data-' + ns + '-result', status);

                    switch (status) {
                        case this.STATUS_VALIDATING:
                            isValidField = null;
                            this.disableSubmitButtons(true);
                            $field.removeClass(this.options.control.valid).removeClass(this.options.control.invalid);
                            $parent.removeClass(this.options.row.valid).removeClass(this.options.row.invalid);
                            if ($icon) {
                                $icon.removeClass(this.options.icon.valid).removeClass(this.options.icon.invalid).addClass(this.options.icon.validating).show();
                            }
                            break;

                        case this.STATUS_INVALID:
                            isValidField = false;
                            this.disableSubmitButtons(true);
                            $field.removeClass(this.options.control.valid).addClass(this.options.control.invalid);
                            $parent.removeClass(this.options.row.valid).addClass(this.options.row.invalid);
                            if ($icon) {
                                $icon.removeClass(this.options.icon.valid).removeClass(this.options.icon.validating).addClass(this.options.icon.invalid).show();
                            }
                            break;

                        case this.STATUS_VALID:
                            // If the field is valid (passes all validators)
                            isValidField = ($allErrors.filter('[data-' + ns + '-result="' + this.STATUS_NOT_VALIDATED +'"]').length === 0)
                                         ? ($allErrors.filter('[data-' + ns + '-result="' + this.STATUS_VALID +'"]').length === $allErrors.length)  // All validators are completed
                                         : null;                                                                                                    // There are some validators that have not done

                            $field.removeClass(this.options.control.valid).removeClass(this.options.control.invalid);
                            if (isValidField !== null) {
                                this.disableSubmitButtons(this.$submitButton ? !this.isValid() : !isValidField);
                                $field.addClass(isValidField ? this.options.control.valid : this.options.control.invalid);
                                if ($icon) {
                                    var isValidating = ($allErrors.filter('[data-' + ns + '-result="' + this.STATUS_VALIDATING +'"]').length > 0);
                                    $icon
                                        .removeClass(this.options.icon.invalid).removeClass(this.options.icon.validating).removeClass(this.options.icon.valid)
                                        .addClass(isValidField ? this.options.icon.valid : (isValidating ? this.options.icon.validating : this.options.icon.invalid))
                                        .show();
                                }
                            }

                            var isValidContainer = this.isValidContainer($parent);
                            if (isValidContainer !== null) {
                                $parent.removeClass(this.options.row.valid).removeClass(this.options.row.invalid).addClass(isValidContainer ? this.options.row.valid : this.options.row.invalid);
                            }
                            break;

                        case this.STATUS_NOT_VALIDATED:
                        /* falls through */
                        default:
                            isValidField = null;
                            this.disableSubmitButtons(false);
                            $field.removeClass(this.options.control.valid).removeClass(this.options.control.invalid);
                            $parent.removeClass(this.options.row.valid).removeClass(this.options.row.invalid);
                            if ($icon) {
                                $icon.removeClass(this.options.icon.valid).removeClass(this.options.icon.invalid).removeClass(this.options.icon.validating).hide();
                            }
                            break;
                    }

                    if ($icon && ('tooltip' === container || 'popover' === container)) {
                        (isValidField === false)
                            // Only show the first error message
                            ? this._createTooltip($field, $allErrors.filter('[data-' + ns + '-result="' + that.STATUS_INVALID + '"]').eq(0).html(), container)
                            : this._destroyTooltip($field, container);
                    } else {
                        (status === this.STATUS_INVALID) ? $errors.show() : $errors.hide();
                    }

                    // Trigger an event
                    $field.trigger($.Event(this.options.events.fieldStatus), {
                        bv: this,   // Support backward
                        fv: this,
                        field: field,
                        element: $field,
                        status: status
                    });
                    this._onFieldValidated($field, validatorName);
                }

                return this;
            },

            /**
             * Validate the form
             *
             * @returns {FormValidation.Base}
             */
            validate: function() {
                if (!this.options.fields) {
                    return this;
                }
                this.disableSubmitButtons(true);

                this._submitIfValid = false;
                for (var field in this.options.fields) {
                    this.validateField(field);
                }

                this._submit();
                this._submitIfValid = true;

                return this;
            },

            /**
             * Validate given field
             *
             * @param {String|jQuery} field The field name or field element
             * @returns {FormValidation.Base}
             */
            validateField: function(field) {
                var ns     = this._namespace,
                    fields = $([]);
                switch (typeof field) {
                    case 'object':
                        fields = field;
                        field  = field.attr('data-' + ns + '-field');
                        break;
                    case 'string':
                        fields = this.getFieldElements(field);
                        break;
                    default:
                        break;
                }

                if (fields.length === 0 || !this.options.fields[field] || this.options.fields[field].enabled === false) {
                    return this;
                }

                var that       = this,
                    type       = fields.attr('type'),
                    total      = ('radio' === type || 'checkbox' === type) ? 1 : fields.length,
                    updateAll  = ('radio' === type || 'checkbox' === type),
                    validators = this.options.fields[field].validators,
                    verbose    = this.isOptionEnabled(field, 'verbose'),
                    validatorName,
                    validateResult;

                for (var i = 0; i < total; i++) {
                    var $field = fields.eq(i);
                    if (this._isExcluded($field)) {
                        continue;
                    }

                    var stop = false;
                    for (validatorName in validators) {
                        if ($field.data(ns + '.dfs.' + validatorName)) {
                            $field.data(ns + '.dfs.' + validatorName).reject();
                        }
                        if (stop) {
                            break;
                        }

                        // Don't validate field if it is already done
                        var result = $field.data(ns + '.result.' + validatorName);
                        if (result === this.STATUS_VALID || result === this.STATUS_INVALID) {
                            this._onFieldValidated($field, validatorName);
                            continue;
                        } else if (validators[validatorName].enabled === false) {
                            this.updateStatus(updateAll ? field : $field, this.STATUS_VALID, validatorName);
                            continue;
                        }

                        $field.data(ns + '.result.' + validatorName, this.STATUS_VALIDATING);
                        validateResult = FormValidation.Validator[validatorName].validate(this, $field, validators[validatorName]);

                        // validateResult can be a $.Deferred object ...
                        if ('object' === typeof validateResult && validateResult.resolve) {
                            this.updateStatus(updateAll ? field : $field, this.STATUS_VALIDATING, validatorName);
                            $field.data(ns + '.dfs.' + validatorName, validateResult);

                            validateResult.done(function($f, v, response) {
                                // v is validator name
                                $f.removeData(ns + '.dfs.' + v).data(ns + '.response.' + v, response);
                                if (response.message) {
                                    that.updateMessage($f, v, response.message);
                                }

                                that.updateStatus(updateAll ? $f.attr('data-' + ns + '-field') : $f, response.valid ? that.STATUS_VALID : that.STATUS_INVALID, v);

                                if (response.valid && that._submitIfValid === true) {
                                    // If a remote validator returns true and the form is ready to submit, then do it
                                    that._submit();
                                } else if (!response.valid && !verbose) {
                                    stop = true;
                                }
                            });
                        }
                        // ... or object { valid: true/false, message: 'dynamic message', otherKey: value, ... }
                        else if ('object' === typeof validateResult && validateResult.valid !== undefined) {
                            $field.data(ns + '.response.' + validatorName, validateResult);
                            if (validateResult.message) {
                                this.updateMessage(updateAll ? field : $field, validatorName, validateResult.message);
                            }
                            this.updateStatus(updateAll ? field : $field, validateResult.valid ? this.STATUS_VALID : this.STATUS_INVALID, validatorName);
                            if (!validateResult.valid && !verbose) {
                                break;
                            }
                        }
                        // ... or a boolean value
                        else if ('boolean' === typeof validateResult) {
                            $field.data(ns + '.response.' + validatorName, validateResult);
                            this.updateStatus(updateAll ? field : $field, validateResult ? this.STATUS_VALID : this.STATUS_INVALID, validatorName);
                            if (!validateResult && !verbose) {
                                break;
                            }
                        }
                    }
                }

                return this;
            },

            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            // Useful APIs which aren't used internally
            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            /**
             * Add a new field
             *
             * @param {String|jQuery} field The field name or field element
             * @param {Object} [options] The validator rules
             * @returns {FormValidation.Base}
             */
            addField: function(field, options) {
                var ns     = this._namespace,
                    fields = $([]);
                switch (typeof field) {
                    case 'object':
                        fields = field;
                        field  = field.attr('data-' + ns + '-field') || field.attr('name');
                        break;
                    case 'string':
                        delete this._cacheFields[field];
                        fields = this.getFieldElements(field);
                        break;
                    default:
                        break;
                }

                fields.attr('data-' + ns + '-field', field);

                var type  = fields.attr('type'),
                    total = ('radio' === type || 'checkbox' === type) ? 1 : fields.length;

                for (var i = 0; i < total; i++) {
                    var $field = fields.eq(i);

                    // Try to parse the options from HTML attributes
                    var opts = this._parseOptions($field);
                    opts = (opts === null) ? options : $.extend(true, options, opts);

                    this.options.fields[field] = $.extend(true, this.options.fields[field], opts);

                    // Update the cache
                    this._cacheFields[field] = this._cacheFields[field] ? this._cacheFields[field].add($field) : $field;

                    // Init the element
                    this._initField(('checkbox' === type || 'radio' === type) ? field : $field);
                }

                this.disableSubmitButtons(false);
                // Trigger an event
                this.$form.trigger($.Event(this.options.events.fieldAdded), {
                    field: field,
                    element: fields,
                    options: this.options.fields[field]
                });

                return this;
            },

            /**
             * Destroy the plugin
             * It will remove all error messages, feedback icons and turn off the events
             */
            destroy: function() {
                var ns = this._namespace, i, field, fields, $field, validator, $icon, row;

                // Destroy the validators first
                for (field in this.options.fields) {
                    fields = this.getFieldElements(field);
                    for (i = 0; i < fields.length; i++) {
                        $field = fields.eq(i);
                        for (validator in this.options.fields[field].validators) {
                            if ($field.data(ns + '.dfs.' + validator)) {
                                $field.data(ns + '.dfs.' + validator).reject();
                            }
                            $field.removeData(ns + '.result.' + validator)
                                  .removeData(ns + '.response.' + validator)
                                  .removeData(ns + '.dfs.' + validator);

                            // Destroy the validator
                            if ('function' === typeof FormValidation.Validator[validator].destroy) {
                                FormValidation.Validator[validator].destroy(this, $field, this.options.fields[field].validators[validator]);
                            }
                        }
                    }
                }

                // Remove messages and icons
                for (field in this.options.fields) {
                    fields = this.getFieldElements(field);
                    row    = this.options.fields[field].row || this.options.row.selector;
                    for (i = 0; i < fields.length; i++) {
                        $field = fields.eq(i);
                        $field
                            // Remove all error messages
                            .data(ns + '.messages')
                                .find('.' + this.options.err.clazz.split(' ').join('.') + '[data-' + ns + '-validator][data-' + ns + '-for="' + field + '"]').remove().end()
                                .end()
                            .removeData(ns + '.messages')
                            // Remove feedback classes
                            .closest(row)
                                .removeClass(this.options.row.valid)
                                .removeClass(this.options.row.invalid)
                                .removeClass(this.options.row.feedback)
                                .end()
                            // Turn off events
                            .off('.' + ns)
                            .removeAttr('data-' + ns + '-field');

                        // Remove feedback icons, tooltip/popover container
                        // Support backward
                        var container = ('function' === typeof (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container))
                                        ? (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container).call(this, $field, this)
                                        : (this.options.fields[field].container || this.options.fields[field].err || this.options.err.container);
                        if ('tooltip' === container || 'popover' === container) {
                            this._destroyTooltip($field, container);
                        }

                        $icon = $field.data(ns + '.icon');
                        if ($icon) {
                            $icon.remove();
                        }
                        $field.removeData(ns + '.icon')
                              // It's safe to remove trigger data here, because it might be used when destroying the validator
                              .removeData(ns + '.trigger');
                    }
                }

                // Destroy the add-ons
                for (var addOn in this.options.addOns) {
                    if ('function' === typeof FormValidation.AddOn[addOn].destroy) {
                        FormValidation.AddOn[addOn].destroy(this, this.options.addOns[addOn]);
                    }
                }

                this.disableSubmitButtons(false);   // Enable submit buttons
                this.$hiddenButton.remove();        // Remove the hidden button

                this.$form
                    .removeClass(this.options.elementClass)
                    .off('.' + ns)
                    .removeData('bootstrapValidator')   // Support backward
                    .removeData('formValidation')
                    // Remove generated hidden elements
                    .find('[data-' + ns + '-submit-hidden]').remove().end()
                    .find('[type="submit"]')
                        .off('click.' + ns);
            },

            /**
             * Enable/Disable all validators to given field
             *
             * @param {String} field The field name
             * @param {Boolean} enabled Enable/Disable field validators
             * @param {String} [validatorName] The validator name. If null, all validators will be enabled/disabled
             * @returns {FormValidation.Base}
             */
            enableFieldValidators: function(field, enabled, validatorName) {
                var validators = this.options.fields[field].validators;

                // Enable/disable particular validator
                if (validatorName
                    && validators
                    && validators[validatorName] && validators[validatorName].enabled !== enabled)
                {
                    this.options.fields[field].validators[validatorName].enabled = enabled;
                    this.updateStatus(field, this.STATUS_NOT_VALIDATED, validatorName);
                }
                // Enable/disable all validators
                else if (!validatorName && this.options.fields[field].enabled !== enabled) {
                    this.options.fields[field].enabled = enabled;
                    for (var v in validators) {
                        this.enableFieldValidators(field, enabled, v);
                    }
                }

                return this;
            },

            /**
             * Some validators have option which its value is dynamic.
             * For example, the zipCode validator has the country option which might be changed dynamically by a select element.
             *
             * @param {jQuery|String} field The field name or element
             * @param {String|Function} option The option which can be determined by:
             * - a string
             * - name of field which defines the value
             * - name of function which returns the value
             * - a function returns the value
             *
             * The callback function has the format of
             *      callback: function(value, validator, $field) {
             *          // value is the value of field
             *          // validator is the BootstrapValidator instance
             *          // $field is the field element
             *      }
             *
             * @returns {String}
             */
            getDynamicOption: function(field, option) {
                var $field = ('string' === typeof field) ? this.getFieldElements(field) : field,
                    value  = $field.val();

                // Option can be determined by
                // ... a function
                if ('function' === typeof option) {
                    return FormValidation.Helper.call(option, [value, this, $field]);
                }
                // ... value of other field
                else if ('string' === typeof option) {
                    var $f = this.getFieldElements(option);
                    if ($f.length) {
                        return $f.val();
                    }
                    // ... return value of callback
                    else {
                        return FormValidation.Helper.call(option, [value, this, $field]) || option;
                    }
                }

                return null;
            },

            /**
             * Get the form element
             *
             * @returns {jQuery}
             */
            getForm: function() {
                return this.$form;
            },

            /**
             * Get the list of invalid fields
             *
             * @returns {jQuery[]}
             */
            getInvalidFields: function() {
                return this.$invalidFields;
            },

            /**
             * Get the current locale
             *
             * @return {String}
             */
            getLocale: function() {
                return this.options.locale;
            },

            /**
             * Get the error messages
             *
             * @param {String|jQuery} [field] The field name or field element
             * If the field is not defined, the method returns all error messages of all fields
             * @param {String} [validator] The name of validator
             * If the validator is not defined, the method returns error messages of all validators
             * @returns {String[]}
             */
            getMessages: function(field, validator) {
                var that     = this,
                    ns       = this._namespace,
                    messages = [],
                    $fields  = $([]);

                switch (true) {
                    case (field && 'object' === typeof field):
                        $fields = field;
                        break;
                    case (field && 'string' === typeof field):
                        var f = this.getFieldElements(field);
                        if (f.length > 0) {
                            var type = f.attr('type');
                            $fields = ('radio' === type || 'checkbox' === type) ? f.eq(0) : f;
                        }
                        break;
                    default:
                        $fields = this.$invalidFields;
                        break;
                }

                var filter = validator ? '[data-' + ns + '-validator="' + validator + '"]' : '';
                $fields.each(function() {
                    messages = messages.concat(
                        $(this)
                            .data(ns + '.messages')
                            .find('.' + that.options.err.clazz + '[data-' + ns + '-for="' + $(this).attr('data-' + ns + '-field') + '"][data-' + ns + '-result="' + that.STATUS_INVALID + '"]' + filter)
                            .map(function() {
                                var v = $(this).attr('data-' + ns + '-validator'),
                                    f = $(this).attr('data-' + ns + '-for');
                                return (that.options.fields[f].validators[v].enabled === false) ? '' : $(this).html();
                            })
                            .get()
                    );
                });

                return messages;
            },

            /**
             * Returns the clicked submit button
             *
             * @returns {jQuery}
             */
            getSubmitButton: function() {
                return this.$submitButton;
            },

            /**
             * Remove a given field
             *
             * @param {String|jQuery} field The field name or field element
             * @returns {FormValidation.Base}
             */
            removeField: function(field) {
                var ns     = this._namespace,
                    fields = $([]);
                switch (typeof field) {
                    case 'object':
                        fields = field;
                        field  = field.attr('data-' + ns + '-field') || field.attr('name');
                        fields.attr('data-' + ns + '-field', field);
                        break;
                    case 'string':
                        fields = this.getFieldElements(field);
                        break;
                    default:
                        break;
                }

                if (fields.length === 0) {
                    return this;
                }

                var type  = fields.attr('type'),
                    total = ('radio' === type || 'checkbox' === type) ? 1 : fields.length;

                for (var i = 0; i < total; i++) {
                    var $field = fields.eq(i);

                    // Remove from the list of invalid fields
                    this.$invalidFields = this.$invalidFields.not($field);

                    // Update the cache
                    this._cacheFields[field] = this._cacheFields[field].not($field);
                }

                if (!this._cacheFields[field] || this._cacheFields[field].length === 0) {
                    delete this.options.fields[field];
                }
                if ('checkbox' === type || 'radio' === type) {
                    this._initField(field);
                }

                this.disableSubmitButtons(false);
                // Trigger an event
                this.$form.trigger($.Event(this.options.events.fieldRemoved), {
                    field: field,
                    element: fields
                });

                return this;
            },

            /**
             * Reset given field
             *
             * @param {String|jQuery} field The field name or field element
             * @param {Boolean} [resetValue] If true, the method resets field value to empty or remove checked/selected attribute (for radio/checkbox)
             * @returns {FormValidation.Base}
             */
            resetField: function(field, resetValue) {
                var ns      = this._namespace,
                    $fields = $([]);
                switch (typeof field) {
                    case 'object':
                        $fields = field;
                        field   = field.attr('data-' + ns + '-field');
                        break;
                    case 'string':
                        $fields = this.getFieldElements(field);
                        break;
                    default:
                        break;
                }

                var total = $fields.length;
                if (this.options.fields[field]) {
                    for (var i = 0; i < total; i++) {
                        for (var validator in this.options.fields[field].validators) {
                            $fields.eq(i).removeData(ns + '.dfs.' + validator);
                        }
                    }
                }

                // Mark field as not validated yet
                this.updateStatus(field, this.STATUS_NOT_VALIDATED);

                if (resetValue) {
                    var type = $fields.attr('type');
                    ('radio' === type || 'checkbox' === type) ? $fields.removeAttr('checked').removeAttr('selected') : $fields.val('');
                }

                return this;
            },

            /**
             * Reset the form
             *
             * @param {Boolean} [resetValue] If true, the method resets field value to empty or remove checked/selected attribute (for radio/checkbox)
             * @returns {FormValidation.Base}
             */
            resetForm: function(resetValue) {
                for (var field in this.options.fields) {
                    this.resetField(field, resetValue);
                }

                this.$invalidFields = $([]);
                this.$submitButton  = null;

                // Enable submit buttons
                this.disableSubmitButtons(false);

                return this;
            },

            /**
             * Revalidate given field
             * It's used when you need to revalidate the field which its value is updated by other plugin
             *
             * @param {String|jQuery} field The field name of field element
             * @returns {FormValidation.Base}
             */
            revalidateField: function(field) {
                this.updateStatus(field, this.STATUS_NOT_VALIDATED)
                    .validateField(field);

                return this;
            },

            /**
             * Set the locale
             *
             * @param {String} locale The locale in format of countrycode_LANGUAGECODE
             * @returns {FormValidation.Base}
             */
            setLocale: function(locale) {
                this.options.locale = locale;
                this.$form.trigger($.Event(this.options.events.localeChanged), {
                    locale: locale,
                    bv: this,   // Support backward
                    fv: this
                });

                return this;
            },

            /**
             * Update the option of a specific validator
             *
             * @param {String|jQuery} field The field name or field element
             * @param {String} validator The validator name
             * @param {String} option The option name
             * @param {String} value The value to set
             * @returns {FormValidation.Base}
             */
            updateOption: function(field, validator, option, value) {
                var ns = this._namespace;
                if ('object' === typeof field) {
                    field = field.attr('data-' + ns + '-field');
                }
                if (this.options.fields[field] && this.options.fields[field].validators[validator]) {
                    this.options.fields[field].validators[validator][option] = value;
                    this.updateStatus(field, this.STATUS_NOT_VALIDATED, validator);
                }

                return this;
            },

            /**
             * Validate given container
             * It can be used with isValidContainer() when you want to work with wizard form
             *
             * @param {String|jQuery} container The container selector or element
             * @returns {FormValidation.Base}
             */
            validateContainer: function(container) {
                var that       = this,
                    ns         = this._namespace,
                    map        = {},
                    $container = ('string' === typeof container) ? $(container) : container;
                if ($container.length === 0) {
                    return this;
                }

                $container.find('[data-' + ns + '-field]').each(function() {
                    var $field = $(this),
                        field  = $field.attr('data-' + ns + '-field');
                    if (!that._isExcluded($field) && !map[field]) {
                        map[field] = $field;
                    }
                });

                for (var field in map) {
                    this.validateField(map[field]);
                }

                return this;
            }
        };

        // Plugin definition
        $.fn.formValidation = function(option) {
            var params = arguments;
            return this.each(function() {
                var $this   = $(this),
                    data    = $this.data('formValidation'),
                    options = 'object' === typeof option && option;
                if (!data) {
                    var framework = (options.framework || $this.attr('data-fv-framework') || 'bootstrap').toLowerCase();
                    switch (framework) {
                        case 'foundation':
                            if (!FormValidation.Framework.Foundation) {
                                throw "Please include Foundation framework";
                            }
                            data = new FormValidation.Framework.Foundation(this, options);
                            break;

                        case 'pure':
                            data = new FormValidation.Framework.Pure(this, options);
                            if (!FormValidation.Framework.Pure) {
                                throw "Please include Pure framework";
                            }
                            break;

                        case 'semantic':
                            if (!FormValidation.Framework.Semantic) {
                                throw "Please include Semantic framework";
                            }
                            data = new FormValidation.Framework.Semantic(this, options);
                            break;

                        case 'uikit':
                            if (!FormValidation.Framework.UIKit) {
                                throw "Please include UIKit framework";
                            }
                            data = new FormValidation.Framework.UIKit(this, options);
                            break;

                        case 'bootstrap':
                        /* falls through */
                        default:
                            if (!FormValidation.Framework.Bootstrap) {
                                throw "Please include Bootstrap framework";
                            }
                            data = new FormValidation.Framework.Bootstrap(this, options);
                            break;
                    }

                    $this.addClass('fv-form-' + framework)
                         .data('formValidation', data);
                }

                // Allow to call plugin method
                if ('string' === typeof option) {
                    data[option].apply(data, Array.prototype.slice.call(params, 1));
                }
            });
        };

        $.fn.formValidation.Constructor = FormValidation.Base;

        // The default options
        // Sorted in alphabetical order
        $.fn.formValidation.DEFAULT_OPTIONS = {
            // The first invalid field will be focused automatically
            autoFocus: true,

            // The form CSS class
            elementClass: 'fv-form',

            // Use custom event name to avoid window.onerror being invoked by jQuery
            // See #630
            events: {
                // Support backward
                formInit: 'init.form.fv',
                formError: 'err.form.fv',
                formSuccess: 'success.form.fv',
                fieldAdded: 'added.field.fv',
                fieldRemoved: 'removed.field.fv',
                fieldInit: 'init.field.fv',
                fieldError: 'err.field.fv',
                fieldSuccess: 'success.field.fv',
                fieldStatus: 'status.field.fv',
                localeChanged: 'changed.locale.fv',
                validatorError: 'err.validator.fv',
                validatorSuccess: 'success.validator.fv'
            },

            // Indicate fields which won't be validated
            // By default, the plugin will not validate the following kind of fields:
            // - disabled
            // - hidden
            // - invisible
            //
            // The setting consists of jQuery filters. Accept 3 formats:
            // - A string. Use a comma to separate filter
            // - An array. Each element is a filter
            // - An array. Each element can be a callback function
            //      function($field, validator) {
            //          $field is jQuery object representing the field element
            //          validator is the BootstrapValidator instance
            //          return true or false;
            //      }
            //
            // The 3 following settings are equivalent:
            //
            // 1) ':disabled, :hidden, :not(:visible)'
            // 2) [':disabled', ':hidden', ':not(:visible)']
            // 3) [':disabled', ':hidden', function($field) {
            //        return !$field.is(':visible');
            //    }]
            excluded: [':disabled', ':hidden', ':not(:visible)'],

            // Map the field name with validator rules
            fields: null,

            // Live validating option
            // Can be one of 3 values:
            // - enabled: The plugin validates fields as soon as they are changed
            // - disabled: Disable the live validating. The error messages are only shown after the form is submitted
            // - submitted: The live validating is enabled after the form is submitted
            live: 'enabled',

            // Locale in the format of languagecode_COUNTRYCODE
            locale: 'en_US',

            // Default invalid message
            message: 'This value is not valid',

            // The field will not be live validated if its length is less than this number of characters
            threshold: null,

            // Whether to be verbose when validating a field or not.
            // Possible values:
            // - true:  when a field has multiple validators, all of them will be checked, and respectively - if errors occur in
            //          multiple validators, all of them will be displayed to the user
            // - false: when a field has multiple validators, validation for this field will be terminated upon the first encountered error.
            //          Thus, only the very first error message related to this field will be displayed to the user
            verbose: true,

            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            // These options mostly are overridden by specific framework
            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            button: {
                // The submit buttons selector
                // These buttons will be disabled to prevent the valid form from multiple submissions
                selector: '[type="submit"]',

                // The disabled class
                disabled: ''
            },

            control: {
                // The CSS class for valid control
                valid: '',

                // The CSS class for invalid control
                invalid: ''
            },

            err: {
                // The CSS class of each message element
                clazz: '',

                // The error messages container. It can be:
                // - 'tooltip' if you want to use Bootstrap tooltip to show error messages
                // - 'popover' if you want to use Bootstrap popover to show error messages
                // - a CSS selector indicating the container
                // In the first two cases, since the tooltip/popover should be small enough, the plugin only shows only one error message
                // You also can define the message container for particular field
                container: null,

                // Used to determine where the messages are placed
                parent: null
            },

            // Shows ok/error/loading icons based on the field validity.
            icon: {
                valid: null,
                invalid: null,
                validating: null,
                feedback: ''
            },

            row: {
                // The CSS selector for indicating the element consists of the field
                // You should adjust this option if your form group consists of many fields which not all of them need to be validated
                selector: null,
                valid: '',
                invalid: '',
                feedback: ''
            }
        };
    }(jQuery));

    return FormValidation;
}))