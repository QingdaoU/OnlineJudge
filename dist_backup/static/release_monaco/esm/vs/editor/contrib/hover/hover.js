/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
import './hover.css';
import * as nls from '../../../nls.js';
import { KeyChord } from '../../../base/common/keyCodes.js';
import * as platform from '../../../base/common/platform.js';
import { IOpenerService } from '../../../platform/opener/common/opener.js';
import { IModeService } from '../../common/services/modeService.js';
import { Range } from '../../common/core/range.js';
import { registerEditorAction, registerEditorContribution, EditorAction } from '../../browser/editorExtensions.js';
import { MouseTargetType } from '../../browser/editorBrowser.js';
import { ModesContentHoverWidget } from './modesContentHover.js';
import { ModesGlyphHoverWidget } from './modesGlyphHover.js';
import { dispose } from '../../../base/common/lifecycle.js';
import { registerThemingParticipant } from '../../../platform/theme/common/themeService.js';
import { editorHoverHighlight, editorHoverBackground, editorHoverBorder, textLinkForeground, textCodeBlockBackground } from '../../../platform/theme/common/colorRegistry.js';
import { EditorContextKeys } from '../../common/editorContextKeys.js';
import { MarkdownRenderer } from '../markdown/markdownRenderer.js';
var ModesHoverController = /** @class */ (function () {
    function ModesHoverController(editor, _openerService, _modeService) {
        var _this = this;
        this._openerService = _openerService;
        this._modeService = _modeService;
        this._editor = editor;
        this._toUnhook = [];
        this._isMouseDown = false;
        if (editor.getConfiguration().contribInfo.hover) {
            this._toUnhook.push(this._editor.onMouseDown(function (e) { return _this._onEditorMouseDown(e); }));
            this._toUnhook.push(this._editor.onMouseUp(function (e) { return _this._onEditorMouseUp(e); }));
            this._toUnhook.push(this._editor.onMouseMove(function (e) { return _this._onEditorMouseMove(e); }));
            this._toUnhook.push(this._editor.onMouseLeave(function (e) { return _this._hideWidgets(); }));
            this._toUnhook.push(this._editor.onKeyDown(function (e) { return _this._onKeyDown(e); }));
            this._toUnhook.push(this._editor.onDidChangeModel(function () { return _this._hideWidgets(); }));
            this._toUnhook.push(this._editor.onDidChangeModelDecorations(function () { return _this._onModelDecorationsChanged(); }));
            this._toUnhook.push(this._editor.onDidScrollChange(function (e) {
                if (e.scrollTopChanged || e.scrollLeftChanged) {
                    _this._hideWidgets();
                }
            }));
        }
    }
    Object.defineProperty(ModesHoverController.prototype, "contentWidget", {
        get: function () {
            if (!this._contentWidget) {
                this._createHoverWidget();
            }
            return this._contentWidget;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ModesHoverController.prototype, "glyphWidget", {
        get: function () {
            if (!this._glyphWidget) {
                this._createHoverWidget();
            }
            return this._glyphWidget;
        },
        enumerable: true,
        configurable: true
    });
    ModesHoverController.get = function (editor) {
        return editor.getContribution(ModesHoverController.ID);
    };
    ModesHoverController.prototype._onModelDecorationsChanged = function () {
        this.contentWidget.onModelDecorationsChanged();
        this.glyphWidget.onModelDecorationsChanged();
    };
    ModesHoverController.prototype._onEditorMouseDown = function (mouseEvent) {
        this._isMouseDown = true;
        var targetType = mouseEvent.target.type;
        if (targetType === MouseTargetType.CONTENT_WIDGET && mouseEvent.target.detail === ModesContentHoverWidget.ID) {
            this._hoverClicked = true;
            // mouse down on top of content hover widget
            return;
        }
        if (targetType === MouseTargetType.OVERLAY_WIDGET && mouseEvent.target.detail === ModesGlyphHoverWidget.ID) {
            // mouse down on top of overlay hover widget
            return;
        }
        if (targetType !== MouseTargetType.OVERLAY_WIDGET && mouseEvent.target.detail !== ModesGlyphHoverWidget.ID) {
            this._hoverClicked = false;
        }
        this._hideWidgets();
    };
    ModesHoverController.prototype._onEditorMouseUp = function (mouseEvent) {
        this._isMouseDown = false;
    };
    ModesHoverController.prototype._onEditorMouseMove = function (mouseEvent) {
        var targetType = mouseEvent.target.type;
        var stopKey = platform.isMacintosh ? 'metaKey' : 'ctrlKey';
        if (this._isMouseDown && this._hoverClicked && this.contentWidget.isColorPickerVisible()) {
            return;
        }
        if (targetType === MouseTargetType.CONTENT_WIDGET && mouseEvent.target.detail === ModesContentHoverWidget.ID && !mouseEvent.event[stopKey]) {
            // mouse moved on top of content hover widget
            return;
        }
        if (targetType === MouseTargetType.OVERLAY_WIDGET && mouseEvent.target.detail === ModesGlyphHoverWidget.ID && !mouseEvent.event[stopKey]) {
            // mouse moved on top of overlay hover widget
            return;
        }
        if (this._editor.getConfiguration().contribInfo.hover && targetType === MouseTargetType.CONTENT_TEXT) {
            this.glyphWidget.hide();
            this.contentWidget.startShowingAt(mouseEvent.target.range, false);
        }
        else if (targetType === MouseTargetType.GUTTER_GLYPH_MARGIN) {
            this.contentWidget.hide();
            this.glyphWidget.startShowingAt(mouseEvent.target.position.lineNumber);
        }
        else {
            this._hideWidgets();
        }
    };
    ModesHoverController.prototype._onKeyDown = function (e) {
        if (e.keyCode !== 5 /* Ctrl */ && e.keyCode !== 6 /* Alt */ && e.keyCode !== 57 /* Meta */) {
            // Do not hide hover when Ctrl/Meta is pressed
            this._hideWidgets();
        }
    };
    ModesHoverController.prototype._hideWidgets = function () {
        if (!this._contentWidget || (this._isMouseDown && this._hoverClicked && this._contentWidget.isColorPickerVisible())) {
            return;
        }
        this._glyphWidget.hide();
        this._contentWidget.hide();
    };
    ModesHoverController.prototype._createHoverWidget = function () {
        var renderer = new MarkdownRenderer(this._editor, this._modeService, this._openerService);
        this._contentWidget = new ModesContentHoverWidget(this._editor, renderer);
        this._glyphWidget = new ModesGlyphHoverWidget(this._editor, renderer);
    };
    ModesHoverController.prototype.showContentHover = function (range, focus) {
        this.contentWidget.startShowingAt(range, focus);
    };
    ModesHoverController.prototype.getId = function () {
        return ModesHoverController.ID;
    };
    ModesHoverController.prototype.dispose = function () {
        this._toUnhook = dispose(this._toUnhook);
        if (this._glyphWidget) {
            this._glyphWidget.dispose();
            this._glyphWidget = null;
        }
        if (this._contentWidget) {
            this._contentWidget.dispose();
            this._contentWidget = null;
        }
    };
    ModesHoverController.ID = 'editor.contrib.hover';
    ModesHoverController = __decorate([
        __param(1, IOpenerService),
        __param(2, IModeService)
    ], ModesHoverController);
    return ModesHoverController;
}());
export { ModesHoverController };
var ShowHoverAction = /** @class */ (function (_super) {
    __extends(ShowHoverAction, _super);
    function ShowHoverAction() {
        return _super.call(this, {
            id: 'editor.action.showHover',
            label: nls.localize('showHover', "Show Hover"),
            alias: 'Show Hover',
            precondition: null,
            kbOpts: {
                kbExpr: EditorContextKeys.textFocus,
                primary: KeyChord(2048 /* CtrlCmd */ | 41 /* KEY_K */, 2048 /* CtrlCmd */ | 39 /* KEY_I */)
            }
        }) || this;
    }
    ShowHoverAction.prototype.run = function (accessor, editor) {
        var controller = ModesHoverController.get(editor);
        if (!controller) {
            return;
        }
        var position = editor.getPosition();
        var range = new Range(position.lineNumber, position.column, position.lineNumber, position.column);
        controller.showContentHover(range, true);
    };
    return ShowHoverAction;
}(EditorAction));
registerEditorContribution(ModesHoverController);
registerEditorAction(ShowHoverAction);
// theming
registerThemingParticipant(function (theme, collector) {
    var editorHoverHighlightColor = theme.getColor(editorHoverHighlight);
    if (editorHoverHighlightColor) {
        collector.addRule(".monaco-editor .hoverHighlight { background-color: " + editorHoverHighlightColor + "; }");
    }
    var hoverBackground = theme.getColor(editorHoverBackground);
    if (hoverBackground) {
        collector.addRule(".monaco-editor .monaco-editor-hover { background-color: " + hoverBackground + "; }");
    }
    var hoverBorder = theme.getColor(editorHoverBorder);
    if (hoverBorder) {
        collector.addRule(".monaco-editor .monaco-editor-hover { border: 1px solid " + hoverBorder + "; }");
        collector.addRule(".monaco-editor .monaco-editor-hover .hover-row:not(:first-child):not(:empty) { border-top: 1px solid " + hoverBorder.transparent(0.5) + "; }");
    }
    var link = theme.getColor(textLinkForeground);
    if (link) {
        collector.addRule(".monaco-editor .monaco-editor-hover a { color: " + link + "; }");
    }
    var codeBackground = theme.getColor(textCodeBlockBackground);
    if (codeBackground) {
        collector.addRule(".monaco-editor .monaco-editor-hover code { background-color: " + codeBackground + "; }");
    }
});
