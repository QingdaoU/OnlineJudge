/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import * as nls from '../../../nls.js';
import { dispose } from '../../../base/common/lifecycle.js';
import Event, { Emitter } from '../../../base/common/event.js';
var AbstractKeybindingService = /** @class */ (function () {
    function AbstractKeybindingService(contextKeyService, commandService, telemetryService, notificationService, statusService) {
        this.toDispose = [];
        this._contextKeyService = contextKeyService;
        this._commandService = commandService;
        this._telemetryService = telemetryService;
        this._statusService = statusService;
        this._notificationService = notificationService;
        this._currentChord = null;
        this._currentChordStatusMessage = null;
        this._onDidUpdateKeybindings = new Emitter();
        this.toDispose.push(this._onDidUpdateKeybindings);
    }
    AbstractKeybindingService.prototype.dispose = function () {
        this.toDispose = dispose(this.toDispose);
    };
    Object.defineProperty(AbstractKeybindingService.prototype, "onDidUpdateKeybindings", {
        get: function () {
            return this._onDidUpdateKeybindings ? this._onDidUpdateKeybindings.event : Event.None; // Sinon stubbing walks properties on prototype
        },
        enumerable: true,
        configurable: true
    });
    AbstractKeybindingService.prototype.getDefaultKeybindingsContent = function () {
        return '';
    };
    AbstractKeybindingService.prototype.getDefaultKeybindings = function () {
        return this._getResolver().getDefaultKeybindings();
    };
    AbstractKeybindingService.prototype.getKeybindings = function () {
        return this._getResolver().getKeybindings();
    };
    AbstractKeybindingService.prototype.customKeybindingsCount = function () {
        return 0;
    };
    AbstractKeybindingService.prototype.lookupKeybindings = function (commandId) {
        return this._getResolver().lookupKeybindings(commandId).map(function (item) { return item.resolvedKeybinding; });
    };
    AbstractKeybindingService.prototype.lookupKeybinding = function (commandId) {
        var result = this._getResolver().lookupPrimaryKeybinding(commandId);
        if (!result) {
            return null;
        }
        return result.resolvedKeybinding;
    };
    AbstractKeybindingService.prototype.softDispatch = function (e, target) {
        var keybinding = this.resolveKeyboardEvent(e);
        if (keybinding.isChord()) {
            console.warn('Unexpected keyboard event mapped to a chord');
            return null;
        }
        var firstPart = keybinding.getDispatchParts()[0];
        if (firstPart === null) {
            // cannot be dispatched, probably only modifier keys
            return null;
        }
        var contextValue = this._contextKeyService.getContext(target);
        var currentChord = this._currentChord ? this._currentChord.keypress : null;
        return this._getResolver().resolve(contextValue, currentChord, firstPart);
    };
    AbstractKeybindingService.prototype._dispatch = function (e, target) {
        var _this = this;
        var shouldPreventDefault = false;
        var keybinding = this.resolveKeyboardEvent(e);
        if (keybinding.isChord()) {
            console.warn('Unexpected keyboard event mapped to a chord');
            return null;
        }
        var firstPart = keybinding.getDispatchParts()[0];
        if (firstPart === null) {
            // cannot be dispatched, probably only modifier keys
            return shouldPreventDefault;
        }
        var contextValue = this._contextKeyService.getContext(target);
        var currentChord = this._currentChord ? this._currentChord.keypress : null;
        var keypressLabel = keybinding.getLabel();
        var resolveResult = this._getResolver().resolve(contextValue, currentChord, firstPart);
        if (resolveResult && resolveResult.enterChord) {
            shouldPreventDefault = true;
            this._currentChord = {
                keypress: firstPart,
                label: keypressLabel
            };
            if (this._statusService) {
                this._currentChordStatusMessage = this._statusService.setStatusMessage(nls.localize('first.chord', "({0}) was pressed. Waiting for second key of chord...", keypressLabel));
            }
            return shouldPreventDefault;
        }
        if (this._statusService && this._currentChord) {
            if (!resolveResult || !resolveResult.commandId) {
                this._statusService.setStatusMessage(nls.localize('missing.chord', "The key combination ({0}, {1}) is not a command.", this._currentChord.label, keypressLabel), 10 * 1000 /* 10s */);
                shouldPreventDefault = true;
            }
        }
        if (this._currentChordStatusMessage) {
            this._currentChordStatusMessage.dispose();
            this._currentChordStatusMessage = null;
        }
        this._currentChord = null;
        if (resolveResult && resolveResult.commandId) {
            if (!resolveResult.bubble) {
                shouldPreventDefault = true;
            }
            this._commandService.executeCommand(resolveResult.commandId, resolveResult.commandArgs || {}).done(undefined, function (err) {
                _this._notificationService.warn(err);
            });
            /* __GDPR__
                "workbenchActionExecuted" : {
                    "id" : { "classification": "SystemMetaData", "purpose": "FeatureInsight" },
                    "from": { "classification": "SystemMetaData", "purpose": "FeatureInsight" }
                }
            */
            this._telemetryService.publicLog('workbenchActionExecuted', { id: resolveResult.commandId, from: 'keybinding' });
        }
        return shouldPreventDefault;
    };
    return AbstractKeybindingService;
}());
export { AbstractKeybindingService };
