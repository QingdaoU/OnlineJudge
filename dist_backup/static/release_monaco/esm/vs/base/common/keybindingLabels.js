/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import * as nls from '../../nls.js';
var ModifierLabelProvider = /** @class */ (function () {
    function ModifierLabelProvider(mac, windows, linux) {
        if (linux === void 0) { linux = windows; }
        this.modifierLabels = [null];
        this.modifierLabels[2 /* Macintosh */] = mac;
        this.modifierLabels[1 /* Windows */] = windows;
        this.modifierLabels[3 /* Linux */] = linux;
    }
    ModifierLabelProvider.prototype.toLabel = function (firstPartMod, firstPartKey, chordPartMod, chordPartKey, OS) {
        if (firstPartKey === null && chordPartKey === null) {
            return null;
        }
        return _asString(firstPartMod, firstPartKey, chordPartMod, chordPartKey, this.modifierLabels[OS]);
    };
    return ModifierLabelProvider;
}());
export { ModifierLabelProvider };
/**
 * A label provider that prints modifiers in a suitable format for displaying in the UI.
 */
export var UILabelProvider = new ModifierLabelProvider({
    ctrlKey: '⌃',
    shiftKey: '⇧',
    altKey: '⌥',
    metaKey: '⌘',
    separator: '',
}, {
    ctrlKey: nls.localize('ctrlKey', "Ctrl"),
    shiftKey: nls.localize('shiftKey', "Shift"),
    altKey: nls.localize('altKey', "Alt"),
    metaKey: nls.localize('windowsKey', "Windows"),
    separator: '+',
});
/**
 * A label provider that prints modifiers in a suitable format for ARIA.
 */
export var AriaLabelProvider = new ModifierLabelProvider({
    ctrlKey: nls.localize('ctrlKey.long', "Control"),
    shiftKey: nls.localize('shiftKey.long', "Shift"),
    altKey: nls.localize('altKey.long', "Alt"),
    metaKey: nls.localize('cmdKey.long', "Command"),
    separator: '+',
}, {
    ctrlKey: nls.localize('ctrlKey.long', "Control"),
    shiftKey: nls.localize('shiftKey.long', "Shift"),
    altKey: nls.localize('altKey.long', "Alt"),
    metaKey: nls.localize('windowsKey.long', "Windows"),
    separator: '+',
});
/**
 * A label provider that prints modifiers in a suitable format for Electron Accelerators.
 * See https://github.com/electron/electron/blob/master/docs/api/accelerator.md
 */
export var ElectronAcceleratorLabelProvider = new ModifierLabelProvider({
    ctrlKey: 'Ctrl',
    shiftKey: 'Shift',
    altKey: 'Alt',
    metaKey: 'Cmd',
    separator: '+',
}, {
    ctrlKey: 'Ctrl',
    shiftKey: 'Shift',
    altKey: 'Alt',
    metaKey: 'Super',
    separator: '+',
});
/**
 * A label provider that prints modifiers in a suitable format for user settings.
 */
export var UserSettingsLabelProvider = new ModifierLabelProvider({
    ctrlKey: 'ctrl',
    shiftKey: 'shift',
    altKey: 'alt',
    metaKey: 'cmd',
    separator: '+',
}, {
    ctrlKey: 'ctrl',
    shiftKey: 'shift',
    altKey: 'alt',
    metaKey: 'win',
    separator: '+',
}, {
    ctrlKey: 'ctrl',
    shiftKey: 'shift',
    altKey: 'alt',
    metaKey: 'meta',
    separator: '+',
});
function _simpleAsString(modifiers, key, labels) {
    if (key === null) {
        return '';
    }
    var result = [];
    // translate modifier keys: Ctrl-Shift-Alt-Meta
    if (modifiers.ctrlKey) {
        result.push(labels.ctrlKey);
    }
    if (modifiers.shiftKey) {
        result.push(labels.shiftKey);
    }
    if (modifiers.altKey) {
        result.push(labels.altKey);
    }
    if (modifiers.metaKey) {
        result.push(labels.metaKey);
    }
    // the actual key
    result.push(key);
    return result.join(labels.separator);
}
function _asString(firstPartMod, firstPartKey, chordPartMod, chordPartKey, labels) {
    var result = _simpleAsString(firstPartMod, firstPartKey, labels);
    if (chordPartKey !== null) {
        result += ' ';
        result += _simpleAsString(chordPartMod, chordPartKey, labels);
    }
    return result;
}
