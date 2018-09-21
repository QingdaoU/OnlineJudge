/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { always } from '../../../base/common/async.js';
import { getDomNodePagePosition } from '../../../base/browser/dom.js';
import { Position } from '../../common/core/position.js';
import { Action } from '../../../base/common/actions.js';
import { Emitter } from '../../../base/common/event.js';
var QuickFixContextMenu = /** @class */ (function () {
    function QuickFixContextMenu(_editor, _contextMenuService, _onApplyCodeAction) {
        this._editor = _editor;
        this._contextMenuService = _contextMenuService;
        this._onApplyCodeAction = _onApplyCodeAction;
        this._onDidExecuteCodeAction = new Emitter();
        this.onDidExecuteCodeAction = this._onDidExecuteCodeAction.event;
    }
    QuickFixContextMenu.prototype.show = function (fixes, at) {
        var _this = this;
        var actions = fixes.then(function (value) {
            return value.map(function (action) {
                return new Action(action.command ? action.command.id : action.title, action.title, undefined, true, function () {
                    return always(_this._onApplyCodeAction(action), function () { return _this._onDidExecuteCodeAction.fire(undefined); });
                });
            });
        });
        this._contextMenuService.showContextMenu({
            getAnchor: function () {
                if (Position.isIPosition(at)) {
                    at = _this._toCoords(at);
                }
                return at;
            },
            getActions: function () { return actions; },
            onHide: function () { _this._visible = false; },
            autoSelectFirstItem: true
        });
    };
    Object.defineProperty(QuickFixContextMenu.prototype, "isVisible", {
        get: function () {
            return this._visible;
        },
        enumerable: true,
        configurable: true
    });
    QuickFixContextMenu.prototype._toCoords = function (position) {
        this._editor.revealPosition(position, 1 /* Immediate */);
        this._editor.render();
        // Translate to absolute editor position
        var cursorCoords = this._editor.getScrolledVisiblePosition(this._editor.getPosition());
        var editorCoords = getDomNodePagePosition(this._editor.getDomNode());
        var x = editorCoords.left + cursorCoords.left;
        var y = editorCoords.top + cursorCoords.top + cursorCoords.height;
        return { x: x, y: y };
    };
    return QuickFixContextMenu;
}());
export { QuickFixContextMenu };
