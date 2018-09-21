/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import './progressbar.css';
import { TPromise } from '../../../common/winjs.base.js';
import * as assert from '../../../common/assert.js';
import { $ } from '../../builder.js';
import * as DOM from '../../dom.js';
import { dispose } from '../../../common/lifecycle.js';
import { Color } from '../../../common/color.js';
import { mixin } from '../../../common/objects.js';
var css_done = 'done';
var css_active = 'active';
var css_infinite = 'infinite';
var css_discrete = 'discrete';
var css_progress_container = 'progress-container';
var css_progress_bit = 'progress-bit';
var defaultOpts = {
    progressBarBackground: Color.fromHex('#0E70C0')
};
/**
 * A progress bar with support for infinite or discrete progress.
 */
var ProgressBar = /** @class */ (function () {
    function ProgressBar(container, options) {
        this.options = options || Object.create(null);
        mixin(this.options, defaultOpts, false);
        this.toUnbind = [];
        this.workedVal = 0;
        this.progressBarBackground = this.options.progressBarBackground;
        this.create(container);
    }
    ProgressBar.prototype.create = function (container) {
        var _this = this;
        $(container).div({ 'class': css_progress_container }, function (builder) {
            _this.element = builder.clone();
            builder.div({ 'class': css_progress_bit }).on([DOM.EventType.ANIMATION_START, DOM.EventType.ANIMATION_END, DOM.EventType.ANIMATION_ITERATION], function (e) {
                switch (e.type) {
                    case DOM.EventType.ANIMATION_ITERATION:
                        if (_this.animationStopToken) {
                            _this.animationStopToken(null);
                        }
                        break;
                }
            }, _this.toUnbind);
            _this.bit = builder.getHTMLElement();
        });
        this.applyStyles();
    };
    ProgressBar.prototype.off = function () {
        this.bit.style.width = 'inherit';
        this.bit.style.opacity = '1';
        this.element.removeClass(css_active);
        this.element.removeClass(css_infinite);
        this.element.removeClass(css_discrete);
        this.workedVal = 0;
        this.totalWork = undefined;
    };
    /**
     * Indicates to the progress bar that all work is done.
     */
    ProgressBar.prototype.done = function () {
        return this.doDone(true);
    };
    /**
     * Stops the progressbar from showing any progress instantly without fading out.
     */
    ProgressBar.prototype.stop = function () {
        return this.doDone(false);
    };
    ProgressBar.prototype.doDone = function (delayed) {
        var _this = this;
        this.element.addClass(css_done);
        // let it grow to 100% width and hide afterwards
        if (!this.element.hasClass(css_infinite)) {
            this.bit.style.width = 'inherit';
            if (delayed) {
                TPromise.timeout(200).then(function () { return _this.off(); });
            }
            else {
                this.off();
            }
        }
        else {
            this.bit.style.opacity = '0';
            if (delayed) {
                TPromise.timeout(200).then(function () { return _this.off(); });
            }
            else {
                this.off();
            }
        }
        return this;
    };
    /**
     * Use this mode to indicate progress that has no total number of work units.
     */
    ProgressBar.prototype.infinite = function () {
        this.bit.style.width = '2%';
        this.bit.style.opacity = '1';
        this.element.removeClass(css_discrete);
        this.element.removeClass(css_done);
        this.element.addClass(css_active);
        this.element.addClass(css_infinite);
        return this;
    };
    /**
     * Tells the progress bar the total number of work. Use in combination with workedVal() to let
     * the progress bar show the actual progress based on the work that is done.
     */
    ProgressBar.prototype.total = function (value) {
        this.workedVal = 0;
        this.totalWork = value;
        return this;
    };
    /**
     * Finds out if this progress bar is configured with total work
     */
    ProgressBar.prototype.hasTotal = function () {
        return !isNaN(this.totalWork);
    };
    /**
     * Tells the progress bar that an amount of work has been completed.
     */
    ProgressBar.prototype.worked = function (value) {
        assert.ok(!isNaN(this.totalWork), 'Total work not set');
        value = Number(value);
        assert.ok(!isNaN(value), 'Value is not a number');
        value = Math.max(1, value);
        this.workedVal += value;
        this.workedVal = Math.min(this.totalWork, this.workedVal);
        if (this.element.hasClass(css_infinite)) {
            this.element.removeClass(css_infinite);
        }
        if (this.element.hasClass(css_done)) {
            this.element.removeClass(css_done);
        }
        if (!this.element.hasClass(css_active)) {
            this.element.addClass(css_active);
        }
        if (!this.element.hasClass(css_discrete)) {
            this.element.addClass(css_discrete);
        }
        this.bit.style.width = 100 * (this.workedVal / this.totalWork) + '%';
        return this;
    };
    /**
     * Returns the builder this progress bar is building in.
     */
    ProgressBar.prototype.getContainer = function () {
        return $(this.element);
    };
    ProgressBar.prototype.style = function (styles) {
        this.progressBarBackground = styles.progressBarBackground;
        this.applyStyles();
    };
    ProgressBar.prototype.applyStyles = function () {
        if (this.bit) {
            var background = this.progressBarBackground ? this.progressBarBackground.toString() : null;
            this.bit.style.backgroundColor = background;
        }
    };
    ProgressBar.prototype.dispose = function () {
        this.toUnbind = dispose(this.toUnbind);
    };
    return ProgressBar;
}());
export { ProgressBar };
