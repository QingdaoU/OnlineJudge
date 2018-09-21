/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { createDecorator } from '../../instantiation/common/instantiation.js';
export var IProgressService = createDecorator('progressService');
export var emptyProgressRunner = Object.freeze({
    total: function () { },
    worked: function () { },
    done: function () { }
});
export var emptyProgress = Object.freeze({ report: function () { } });
var Progress = /** @class */ (function () {
    function Progress(callback) {
        this._callback = callback;
    }
    Object.defineProperty(Progress.prototype, "value", {
        get: function () {
            return this._value;
        },
        enumerable: true,
        configurable: true
    });
    Progress.prototype.report = function (item) {
        this._value = item;
        this._callback(this._value);
    };
    return Progress;
}());
export { Progress };
export var ProgressLocation;
(function (ProgressLocation) {
    ProgressLocation[ProgressLocation["Explorer"] = 1] = "Explorer";
    ProgressLocation[ProgressLocation["Scm"] = 3] = "Scm";
    ProgressLocation[ProgressLocation["Extensions"] = 5] = "Extensions";
    ProgressLocation[ProgressLocation["Window"] = 10] = "Window";
})(ProgressLocation || (ProgressLocation = {}));
export var IProgressService2 = createDecorator('progressService2');
